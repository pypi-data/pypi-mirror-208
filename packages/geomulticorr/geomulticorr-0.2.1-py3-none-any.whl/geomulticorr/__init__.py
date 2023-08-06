version = '0.2.1'

# User
try:
    from geomulticorr.session import Open
    
# Developer
except ModuleNotFoundError:
   from src.geomulticorr.session import Open

print(f'''-------------
geomulticorr {version}
-------------''')