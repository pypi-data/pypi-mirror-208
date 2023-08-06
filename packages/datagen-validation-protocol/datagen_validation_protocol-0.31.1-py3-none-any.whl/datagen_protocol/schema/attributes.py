import enum
from enum import Enum


class Ethnicity(str, enum.Enum):
    AFRICAN = "african"
    SOUTH_ASIAN = "south_asian"
    SOUTHEAST_ASIAN = "southeast_asian"
    HISPANIC = "hispanic"
    MEDITERRANEAN = "mediterranean"
    NORTH_EUROPEAN = "north_european"


class Gender(str, enum.Enum):
    FEMALE = "female"
    MALE = "male"


class Age(str, enum.Enum):
    ADULT = "adult"
    OLD = "old"
    YOUNG = "young"


class EyesColor(str, enum.Enum):
    BROWN = "brown"
    GREEN = "green"
    BLUE = "blue"
    HAZEL = "hazel"
    GRAY = "gray"
    AMBER = "amber"


class AccessoryPosition(str, enum.Enum):
    ON_CHIN = "chin"
    ON_MOUTH = "mouth"
    ON_NOSE = "nose"


class GlassesModel(str, enum.Enum):
    GENERAL = "general"


class GlassesBrand(str, enum.Enum):
    GENERAL = "general"


class GlassesStyle(str, enum.Enum):
    AVIATOR = "aviator"
    BROWLINE = "browline"
    CAT_EYE = "cat_eye"
    GEOMETRIC = "geometric"
    OVAL = "oval"
    OVERSIZED = "oversized"
    READING_FULL_FRAME = "reading_full_frame"
    READING_RIMLESS = "reading_rimless"
    ROUND = "round"


class MaskStyle(str, enum.Enum):
    CLOTH = "cloth"


class HairLength(str, enum.Enum):
    BUZZ_CUT = "buzz_cut"
    UNDEFINED = "undefined"
    SHOULDER = "shoulder"
    CHIN = "chin"
    ARMPIT = "armpit"
    EAR = "ear"
    TAILBONE = "tailbone"
    MID_BACK = "mid_back"


class HairStyle(str, enum.Enum):
    LAYERED = "layered"
    UNDEFINED = "undefined"
    HAIR_DOWN = "hair_down"
    BUN = "bun"
    CURTAIN = "curtain"
    BALDING = "balding"
    BANGS = "bangs"
    HIGH_TOP_CUT = "high_top_cut"
    PONYTAIL = "ponytail"
    PULLED_BACK = "pulled_back"
    AFRO = "afro"
    CREW_CUT = "crew_cut"
    BOB = "bob"


class Environment(str, enum.Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    CROSS_POLARIZED = "cross_polarized"


class TimeOfDay(str, enum.Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"
    DAY = "day"
    NA = "N/A"


class Generator(str, enum.Enum):
    IDENTITIES = "identities"
    HIC = "hic"


class FacialHairStyle(str, enum.Enum):
    FULL_BEARD = "full_beard"
    STUBBLE = "stubble"
    MUSTACHE = "mustache"
    BEARD = "beard"
    PARTIAL_BEARD = "partial_beard"


class HICDomain(str, enum.Enum):
    IN_CABIN = "in_cabin"
    SMART_OFFICE = "smart_office"
    HOME_SECURITY = "home_security"
    SMART_FITNESS = "smart_fitness"


class HICSubDomain(str, enum.Enum):
    HOME_OFFICE = "home_office"
    HOME_FITNESS = "home_fitness"
    FRONT_DOOR_CAMERA = "front_door_camera"
    IN_CABIN = "in_cabin"
    MEETING_ROOM = "meeting_room"


class HumanBehaviour(str, enum.Enum):
    BICEPS_CURLS_DUMBBELLS = "biceps_curls_dumbbells"
    BRINGING_MULTI_PACKAGES_TO_THE_FRONT_DOOR = "bringing_multi_packages_to_the_front_door"
    DRIVER_ADJUSTING_MIRROR = "driver_adjusting_mirror"
    DRIVER_BEHAVIORS_PLUS_TODDLER_IN_CAR = "driver_behaviors_plus_toddler_in_car"
    DRIVER_DRESSING = "driver_dressing"
    DRIVER_DRINKING = "driver_drinking"
    DRIVER_EATING = "driver_eating"
    DRIVER_FACE_TOUCHING = "driver_face_touching"
    DRIVER_FALLING_ASLEEP = "driver_falling_asleep"
    DRIVER_LOOKING_AROUND = "driver_looking_around"
    DRIVER_PLAYING_WITH_MOBILE_PHONE = "driver_playing_with_mobile_phone"
    DRIVER_PUT_MAKEUP = "driver_put_makeup"
    DRIVER_SHAVING = "driver_shaving"
    DRIVER_SINGING = "driver_singing"
    DRIVER_SMOKING = "driver_smoking"
    DRIVER_STANDARD_DRIVING_ONE_HAND = "driver_standard_driving_one_hand"
    DRIVER_STANDARD_DRIVING_TWO_HANDS = "driver_standard_driving_two_hands"
    DRIVER_ENTERING_CAR = "driver_entering_car"
    DRIVER_EXITING_CAR = "driver_exiting_car"
    DRIVER_ADJUSTING_BELT = "driver_adjusting_belt"
    DRIVER_ADJUSTING_SEAT = "driver_adjusting_seat"
    DRIVER_TOUCHING_NOSE = "driver_touching_nose"
    PASSENGER_PUT_MAKEUP = "passenger_put_makeup"
    PASSENGER_ADJUSTING_SEAT = "passenger_adjusting_seat"
    PASSENGER_LEANING = "passenger_leaning"
    PASSENGER_LOOKING_FOR_OBJECT = "passenger_looking_for_object"
    PASSENGER_ADJUSTING_BELT = "passenger_adjusting_belt"
    PASSENGER_DISTRACTING_DRIVER = "passenger_distracting_driver"
    PASSENGER_LOOKING_AROUND = "passenger_looking_around"
    PASSENGER_PLAYING_WITH_MOBILE_PHONE = "passenger_playing_with_mobile_phone"
    PASSENGER_ACCESSORIZING = "passenger_accessorizing"
    PASSENGER_EATING = "passenger_eating"
    PASSENGER_DRINKING = "passenger_drinking"
    DRIVER_TURNING_AROUND = "driver_turning_around"
    FALLING_FRONT_STEPS = "falling_front_steps"
    FALLING_MEDICAL_CONDITION = "falling_medical_condition"
    FALLING_UNEVEN_ROAD = "falling_uneven_road"
    FORWARD_CRUNCHES = "forward_crunches"
    GLUTE_BRIDGE = "glute_bridge"
    LOOKING_AWAY_FROM_THE_LAPTOP = "looking_away_from_the_laptop"
    MIX_WITH_PACKAGES_AND_NON_DELIVERY_PACKAGES = "mix_with_packages_and_non_delivery_packages"
    OVERHEAD_SQUATS = "overhead_squats"
    PICKING_A_PACKAGE_FROM_THE_FRONT_DOOR = "picking_a_package_from_the_front_door"
    PLANK_FACE_DOWN = "plank_face_down"
    PUSH_UPS = "pushups"
    ROAD_RAGE = "road_rage"
    SLEEPY_CLOSING_EYES = "sleepy_closing_eyes"
    STANDING_UP_FROM_CHAIR_WALKING_TO_THE_SIDE = "standing_up_from_chair_walking_to_the_side"
    STATIC_LUNGE = "static_lunge"
    TALKING_FACE = "talking_face"
    TALKING_ON_MOBILE_PHONE = "talking_on_mobile_phone"
    TALKING_WHILE_TOUCHING_FACE = "talking_while_touching_face"
    TURNING_BACK_AND_LOOKING_AWAY_WITH_BODY = "turning_back_and_looking_away_with_body"
    WALKING_TO_THE_DOOR_WITH_A_DELIVERY_PACKAGE = "walking_to_the_door_with_a_delivery_package"
    WALKING_TO_THE_DOOR_WITH_PACKAGED_ITEMS = "walking_to_the_door_with_packaged_items"
    TRIP_FALL_OVER_OBJECT = "trip_fall_over_object"
    STANDING_BY_A_WHITE_BOARD = "standing_by_a_white_board"
