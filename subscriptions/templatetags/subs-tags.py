from django import template

register = template.Library()

def dget0(h, key):
  if key in h: return h[key]
  else: return 0
dget0.is_safe = False

register.filter('dget0', dget0)

