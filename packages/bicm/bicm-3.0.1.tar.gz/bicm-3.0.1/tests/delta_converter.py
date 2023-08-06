

def delta_converter(delta):
    if delta.seconds//60==0:
        return str(delta.seconds)+' s'
    elif delta.seconds//3600==0:
        minutes=delta.seconds//60
        seconds=delta.seconds % 60
        return str(minutes)+' m and '+str(seconds)+' s'
    else:
        hours=delta.seconds//3600
        rest=delta.seconds % 3600
        minutes=rest//60
        seconds=resrt % 60
        return str(hours)+' h and '+str(minutes)+' m and '+str(seconds)+' s'