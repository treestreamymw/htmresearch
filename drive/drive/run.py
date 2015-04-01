#!/usr/bin/env python

import argparse

from drive.road import StraightRoad, ZigZagRoad
from drive.field import Field
from drive.vehicle import HumanVehicle, RandomVehicle, LoopVehicle
from drive.sensor import PositionSensor
from drive.motor import AccelerationMotor, PositionMotor
from drive.scorer import StayOnRoadScorer
from drive.model import PositionPredictionModel, PositionBehaviorModel
from drive.logs import Logs
from drive.graphics import Graphics
from drive.plots import Plots, PositionPredictionPlots, PositionBehaviorPlots
from drive.game import Game



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--plots', choices=[None,
                                          "default",
                                          "positionPrediction",
                                          "positionBehavior"],
                      default=None,
                      help="Enable plots")
  parser.add_argument('--disableGraphics', action='store_true',
                      help="Disable graphics")
  parser.add_argument('--motor', choices=["acceleration", "position"],
                      default="acceleration")
  parser.add_argument('--road', choices=["straight", "zigzag"],
                      default="zigzag")
  parser.add_argument('--vehicle', choices=["human", "random", "loop"],
                      default="human")
  parser.add_argument('--model', choices=["positionPrediction",
                                          "positionBehavior"],
                      default="positionBehavior")
  parser.add_argument('--fieldWidth', type=int,
                      default=100)
  parser.add_argument('--sensorNoise', type=float,
                      default=0)
  parser.add_argument('--motorNoise', type=float,
                      default=0)
  parser.add_argument('--goal', type=float,
                      default=None)
  parser.add_argument('--plotEvery', type=int,
                      default=25)
  parser.add_argument('--manualRun', action='store_true',
                      help="Wait for input on each timestep")

  args = parser.parse_args()

  if args.road == "straight":
    road = StraightRoad()
  elif args.road == "zigzag":
    road = ZigZagRoad()

  field = Field(road, width=args.fieldWidth)

  sensorNoise = (0, args.sensorNoise)
  sensor = PositionSensor(noise=sensorNoise)

  motorNoise = (0, args.motorNoise)
  if args.motor == "acceleration":
    motor = AccelerationMotor(noise=motorNoise)
  elif args.motor == "position":
    motor = PositionMotor(noise=motorNoise)

  startPosition = field.width / 2
  if args.vehicle == "human":
    vehicle = HumanVehicle(field, sensor, motor, startPosition=startPosition,
                           motorValues=range(-4, 4+1))
  if args.vehicle == "random":
    vehicle = RandomVehicle(field, sensor, motor, startPosition=startPosition,
                            motorValues=range(-3, 3+1))
  if args.vehicle == "loop":
    vehicle = LoopVehicle(field, sensor, motor, startPosition=startPosition,
                          motorValues=[0, -1, 0, 1, 0, 1, 0, -1])

  scorer = StayOnRoadScorer(field, vehicle)

  if args.model == "positionPrediction":
    model = PositionPredictionModel(tmParams={
      "columnDimensions": [1024],
      "minThreshold": 35,
      "activationThreshold": 35,
      "maxNewSynapseCount": 40,
      "cellsPerColumn": 8,
      "initialPermanence": 0.4,
      "connectedPermanence": 0.6,
      "permanenceIncrement": 0.1,
      "permanenceDecrement": 0.1,
    })
  elif args.model == "positionBehavior":
    model = PositionBehaviorModel(motorValues=vehicle.motorValues,
                                  bmParams={
      "numSensorColumns": 1024,
      "numCellsPerSensorColumn": 16
    })

  plots = None
  if args.plots == "positionPrediction":
    plots = PositionPredictionPlots(field, vehicle, scorer, model)
  if args.plots == "positionBehavior":
    plots = PositionBehaviorPlots(field, vehicle, scorer, model)
  if args.plots == "default":
    plots = Plots(field, vehicle, scorer, model)

  logs = Logs(field, vehicle, scorer, model)

  if args.disableGraphics:
    graphics = None
  else:
    graphics = Graphics(field, vehicle, scorer, model)

  game = Game(field, vehicle, scorer, model, goal=args.goal,
              logs=logs, plots=plots, graphics=graphics,
              plotEvery=args.plotEvery,
              manualRun=args.manualRun)

  if args.vehicle == "human":
    vehicle.setGraphics(game.graphics)

  game.run()
