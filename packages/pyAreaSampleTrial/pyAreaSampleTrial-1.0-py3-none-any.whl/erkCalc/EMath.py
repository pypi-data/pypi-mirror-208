def getFact(n:int) -> int:
    ft = 1
    fn = n + 1
    for i in range(1,fn):
        ft *=i
    return ft

def trpArea(oneP:float,secondP:float,height:float) ->float:
   trp = ((oneP + secondP) / 2) * height
   return trp

def traArea(fEdge:float,height:float) -> float:
    tra = (fEdge * height ) / 2
    return  tra
