#!/usr/bin/env python3
from cereal import car
from math import fabs
from cereal import log
from common.numpy_fast import interp
from selfdrive.config import Conversions as CV
from selfdrive.car.gm.values import CAR, Ecu, ECU_FINGERPRINT, CruiseButtons, \
                                    AccState, FINGERPRINTS, CarControllerParams
from selfdrive.car import STD_CARGO_KG, scale_rot_inertia, scale_tire_stiffness, is_ecu_disconnected, gen_empty_fingerprint, get_safety_config
from selfdrive.car.interfaces import CarInterfaceBase

ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName

class CarInterface(CarInterfaceBase):

  @staticmethod
  def get_pid_accel_limits(CP, current_speed, cruise_speed):
    params = CarControllerParams()
    return params.ACCEL_MIN, params.ACCEL_MAX
  #
  #    v_current_kph = current_speed * CV.MS_TO_KPH
  #
  #    gas_max_bp = [-0.5, 10., 20., 50., 70., 130.]
  #    gas_max_v = [params.ACCEL_MAX, 1.9, 1.7, 0.7, 0.5, 0.3]
  #
  #    brake_max_bp = [-0.5, 20., 30., 50., 70., 130.]
  #    brake_max_v = [params.ACCEL_MIN, -2.5, -2.0, -1.7, -1.2, -1.2]
  #
  #    return interp(v_current_kph, brake_max_bp, brake_max_v), interp(v_current_kph, gas_max_bp, gas_max_v)

  # Volt determined by iteratively plotting and minimizing error for f(angle, speed) = steer.
  @staticmethod
  def get_steer_feedforward_volt(desired_angle, v_ego):
    desired_angle *= 0.02904609
    sigmoid = desired_angle / (1 + fabs(desired_angle))
    return 0.10006696 * sigmoid * (v_ego + 3.12485927)

  @staticmethod
  def get_steer_feedforward_acadia(desired_angle, v_ego):
    desired_angle *= 0.09760208
    sigmoid = desired_angle / (1 + fabs(desired_angle))
    return 0.04689655 * sigmoid * (v_ego + 10.028217)

  def get_steer_feedforward_function(self):
    if self.CP.carFingerprint == CAR.VOLT:
      return self.get_steer_feedforward_volt
    elif self.CP.carFingerprint == CAR.ACADIA:
      return self.get_steer_feedforward_acadia
    else:
      return CarInterfaceBase.get_steer_feedforward_default

  @staticmethod
  def get_params(candidate, fingerprint=gen_empty_fingerprint(), has_relay=False, car_fw=None):
    ret = CarInterfaceBase.get_std_params(candidate, fingerprint, has_relay)
    ret.carName = "gm"
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.gm)]
    ret.pcmCruise = False  # stock cruise control is kept off

    # GM port is a community feature
    # TODO: make a port that uses a car harness and it only intercepts the camera
    ret.communityFeature = True
    ret.dashcamOnly = candidate in {CAR.CADILLAC_ATS, CAR.HOLDEN_ASTRA, CAR.MALIBU}

    # Presence of a camera on the object bus is ok.
    # Have to go to read_only if ASCM is online (ACC-enabled cars),
    # or camera is on powertrain bus (LKA cars without ACC).
    # for white panda
    ret.enableCamera = is_ecu_disconnected(fingerprint[0], FINGERPRINTS, ECU_FINGERPRINT, candidate, Ecu.fwdCamera) or has_relay
    ret.openpilotLongitudinalControl = ret.enableCamera

    tire_stiffness_factor = 0.444  # not optimized yet

    # for autohold on ui icon
    ret.enableAutoHold = 241 in fingerprint[0]

    # Start with a baseline lateral tuning for all GM vehicles. Override tuning as needed in each model section below.
    ret.minSteerSpeed = 7 * CV.MPH_TO_MS
    ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
    ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2], [0.00]]
    ret.lateralTuning.pid.kf = 0.00006   # full torque for 20 deg at 80mph means 0.00007818594
    ret.steerMaxBP = [0., 8.3, 33.]
    ret.steerMaxV = [1.5, 1.4, 1.2]
    ret.steerRateCost = 1.0
    ret.steerActuatorDelay = 0.1

    if candidate == CAR.VOLT:
      # supports stop and go, but initial engage must be above 18mph (which include conservatism)
      ret.minEnableSpeed = -1 * CV.MPH_TO_MS
      ret.mass = 1607. + STD_CARGO_KG
      ret.wheelbase = 2.69
      ret.steerRatio = 17.7
      tire_stiffness_factor = 0.384 # Stock Michelin Energy Saver A/S, LiveParameters
      ret.steerRatioRear = 0.
      ret.centerToFront = ret.wheelbase * 0.45  # wild guess
      ret.lateralTuning.pid.kf = 1. # get_steer_feedforward_volt()
      ret.steerActuatorDelay = 0.2

# D gain
      ret.lateralTuning.pid.kdBP = [0.]
      ret.lateralTuning.pid.kdV = [0.0002]  #corolla from shane fork : 0.725

    elif candidate == CAR.MALIBU:
      # supports stop and go, but initial engage must be above 18mph (which include conservatism)
      ret.minEnableSpeed = 18 * CV.MPH_TO_MS
      ret.mass = 1496. + STD_CARGO_KG
      ret.wheelbase = 2.83
      ret.steerRatio = 15.8
      ret.steerRatioRear = 0.
      ret.centerToFront = ret.wheelbase * 0.4  # wild guess

    elif candidate == CAR.HOLDEN_ASTRA:
      ret.mass = 1363. + STD_CARGO_KG
      ret.wheelbase = 2.662
      # Remaining parameters copied from Volt for now
      ret.centerToFront = ret.wheelbase * 0.4
      ret.minEnableSpeed = 18 * CV.MPH_TO_MS
      ret.steerRatio = 15.7
      ret.steerRatioRear = 0.

    elif candidate == CAR.ACADIA:
      ret.minEnableSpeed = -1.  # engage speed is decided by pcm
      ret.mass = 4353. * CV.LB_TO_KG + STD_CARGO_KG
      ret.wheelbase = 2.86
      ret.steerRatio = 14.4  # end to end is 13.46
      ret.steerRatioRear = 0.
      ret.centerToFront = ret.wheelbase * 0.4

    elif candidate == CAR.BUICK_REGAL:
      ret.minEnableSpeed = 18 * CV.MPH_TO_MS
      ret.mass = 3779. * CV.LB_TO_KG + STD_CARGO_KG  # (3849+3708)/2
      ret.wheelbase = 2.83  # 111.4 inches in meters
      ret.steerRatio = 14.4  # guess for tourx
      ret.steerRatioRear = 0.
      ret.centerToFront = ret.wheelbase * 0.4  # guess for tourx

    elif candidate == CAR.CADILLAC_ATS:
      ret.minEnableSpeed = 18 * CV.MPH_TO_MS
      ret.mass = 1601. + STD_CARGO_KG
      ret.wheelbase = 2.78
      ret.steerRatio = 15.3
      ret.steerRatioRear = 0.
      ret.centerToFront = ret.wheelbase * 0.49

    elif candidate == CAR.ESCALADE_ESV:
      ret.minEnableSpeed = -1.  # engage speed is decided by pcm
      ret.mass = 2739. + STD_CARGO_KG
      ret.wheelbase = 3.302
      ret.steerRatio = 17.3
      ret.centerToFront = ret.wheelbase * 0.49
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[10., 41.0], [10., 41.0]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.13, 0.24], [0.01, 0.02]]
      ret.lateralTuning.pid.kf = 0.000045
      tire_stiffness_factor = 1.0

    # TODO: get actual value, for now starting with reasonable value for
    # civic and scaling by mass and wheelbase
    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)

    # TODO: start from empirically derived lateral slip stiffness for the civic and scale by
    # mass and CG position, so all cars will have approximately similar dyn behaviors
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront, \
        tire_stiffness_factor=tire_stiffness_factor)

    ret.stoppingControl = True

    ret.longitudinalTuning.deadzoneBP = [0., 100.*CV.KPH_TO_MS]
    ret.longitudinalTuning.deadzoneV = [0.0, .14]

    # Comma's kp, ki
    # ret.longitudinalTuning.kpBP = [5., 35.]
    # ret.longitudinalTuning.kpV = [2.4, 1.5]
    # ret.longitudinalTuning.kiBP = [0.]
    # ret.longitudinalTuning.kiV = [0.36]
    # Volt's kp, ki
    ret.longitudinalTuning.kpBP = [-0.5, 5.6, 8.3, 13.9, 19.4, 33.]
    ret.longitudinalTuning.kpV = [4.2, 3.8, 1.9, 1.5, 0.8, 0.4]
    ret.longitudinalTuning.kiBP = [-0.5, 5.6, 8.4, 13.9, 19.4, 33.]
    ret.longitudinalTuning.kiV = [0.5, 0.53, 0.62, 0.68, 0.36, 0.3]
    ret.longitudinalTuning.kdBP = [0., 5., 33.]
    ret.longitudinalTuning.kdV = [1.3, 0.8, 0.2]
    # ret.startAccel = 0.8 #starting 단계에서 이 수치까지 초당 startingAccelRate로 가속
    ret.stopAccel = -2.0 #stopping 단계에서 이수치까지 초당 stoppingDecelRate로 감속
    # ret.startingAccelRate = 9.6 # startAccel에 도달하기 위한 가속비
    ret.stoppingDecelRate = 2.4 # stopAccel에 도달하기 위한 감속비
    ret.vEgoStopping = 0.28 # 앞차 속도가 이 수치보다 작으면 pid에서 stopping으로 바뀜
    ret.vEgoStarting = 0.26 # 앞차 속도가 이 수치보다 커야 stopping에서 starting으로 옮김
    ret.steerLimitTimer = 2.5
    ret.radarTimeStep = 0.0667  # GM radar runs at 15Hz instead of standard 20Hz

    return ret

  # returns a car.CarState
  def update(self, c, can_strings):
    self.cp.update_strings(can_strings)
    self.cp_loopback.update_strings(can_strings) # GM: EPS fault workaround (#22404)
    # bellow two lines for Brake Light
    self.cp_chassis.update_strings(can_strings)
    ret = self.CS.update(self.cp, self.cp_loopback, self.cp_chassis) # GM: EPS fault workaround (#22404)

    #brake autohold
    if not self.CS.autoholdBrakeStart and self.CS.brakePressVal > 40.0:
      self.CS.autoholdBrakeStart = True

    cruiseEnabled = self.CS.pcm_acc_status != AccState.OFF
    ret.cruiseState.enabled = cruiseEnabled

    ret.cruiseGap = self.CS.follow_level

    ret.canValid = self.cp.can_valid and self.cp_loopback.can_valid # GM: EPS fault workaround (#22404)
    ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False
    #for RPM
    ret.engineRPM = self.CS.engineRPM

    buttonEvents = []

    if self.CS.cruise_buttons != self.CS.prev_cruise_buttons and self.CS.prev_cruise_buttons != CruiseButtons.INIT:
      be = car.CarState.ButtonEvent.new_message()
      be.type = ButtonType.unknown
      if self.CS.cruise_buttons != CruiseButtons.UNPRESS:
        be.pressed = True
        but = self.CS.cruise_buttons
      else:
        be.pressed = False
        but = self.CS.prev_cruise_buttons
      if but == CruiseButtons.RES_ACCEL:
        if not (ret.cruiseState.enabled and ret.standstill):
          be.type = ButtonType.accelCruise  # Suppress resume button if we're resuming from stop so we don't adjust speed.
      elif but == CruiseButtons.SET_DECEL:
        if not cruiseEnabled and not self.CS.lkMode:
          self.lkMode = True
        be.type = ButtonType.decelCruise
      elif but == CruiseButtons.CANCEL:
        be.type = ButtonType.cancel
      elif but == CruiseButtons.MAIN:
        be.type = ButtonType.altButton3
      buttonEvents.append(be)

    ret.buttonEvents = buttonEvents

    if cruiseEnabled and self.CS.lka_button and self.CS.lka_button != self.CS.prev_lka_button:
      self.CS.lkMode = not self.CS.lkMode

    if self.CS.distance_button and self.CS.distance_button != self.CS.prev_distance_button:
       self.CS.follow_level -= 1
       if self.CS.follow_level < 1:
         self.CS.follow_level = 3

    events = self.create_common_events(ret, pcm_enable=False)

    if ret.vEgo < self.CP.minEnableSpeed and self.CS.pcm_acc_status != AccState.ACTIVE:
      events.add(EventName.belowEngageSpeed)
    if self.CS.park_brake:
      events.add(EventName.parkBrake)
	#autohold event
    if self.CS.autoHoldActivated:
      events.add(car.CarEvent.EventName.autoHoldActivated)

    # handle button presses
    for b in ret.buttonEvents:
      # do enable on both accel and decel buttons
      if b.type in [ButtonType.accelCruise, ButtonType.decelCruise] and not b.pressed:
        events.add(EventName.buttonEnable)
      # do disable on button down
      if b.type == ButtonType.cancel and b.pressed:
        events.add(EventName.buttonCancel)

    ret.events = events.to_msg()

    # copy back carState packet to CS
    self.CS.out = ret.as_reader()

    return self.CS.out

    events = self.create_common_events(ret, pcm_enable=False)

    if ret.vEgo < self.CP.minEnableSpeed:
      events.add(EventName.belowEngageSpeed)
    if self.CS.park_brake:
      events.add(EventName.parkBrake)
    if ret.cruiseState.standstill:
      events.add(EventName.resumeRequired)

    # autohold on ui icon
    if self.CS.autoHoldActivated == True:
      ret.autoHoldActivated = 1

    if self.CS.autoHoldActivated == False:
      ret.autoHoldActivated = 0

    # handle button presses
    for b in ret.buttonEvents:
      # do enable on both accel and decel buttons
      if b.type in [ButtonType.accelCruise, ButtonType.decelCruise] and not b.pressed:
        events.add(EventName.buttonEnable)
      # do disable on button down
      if b.type == ButtonType.cancel and b.pressed:
        events.add(EventName.buttonCancel)

    ret.events = events.to_msg()

    # copy back carState packet to CS
    self.CS.out = ret.as_reader()

    return self.CS.out

  def apply(self, c):
    hud_control = c.hudControl
    hud_v_cruise = hud_control.setSpeed
    if hud_v_cruise > 70:
      hud_v_cruise = 0

    # For Openpilot, "enabled" includes pre-enable.
    # In GM, PCM faults out if ACC command overlaps user gas.
    enabled = c.enabled and not self.CS.out.gasPressed

    ret = self.CC.update(enabled, self.CS, self.frame,
                         c.actuators,
                         hud_v_cruise, c.hudControl.lanesVisible,
                         c.hudControl.leadVisible, c.hudControl.visualAlert)

    self.frame += 1

    # Release Auto Hold and creep smoothly when regenpaddle pressed
    if (self.CS.regenPaddlePressed or (self.CS.brakePressVal > 9.0 and self.CS.prev_brakePressVal < self.CS.brakePressVal)) and self.CS.autoHold:
      self.CS.autoHoldActive = False
      self.CS.autoholdBrakeStart = False

    if self.CS.autoHold and not self.CS.autoHoldActive and not self.CS.regenPaddlePressed:
      if self.CS.out.vEgo > 0.02:
        self.CS.autoHoldActive = True
      elif self.CS.out.vEgo < 0.01 and self.CS.out.brakePressed:
        self.CS.autoHoldActive = True
    return ret
