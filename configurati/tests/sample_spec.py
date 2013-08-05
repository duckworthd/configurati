from configurati import required, optional


a = required(type=int)
b = optional(type=float, default=1.0)
c = {
  'd': required(type=str),
  'e': [required(type=str)]
}
