import math

def make_heuristics(coords, goals):
  goal_pts = [coords[goal] for goal in goals]
  def h(n):
      # n is the current node's coordinates
      (x,y) = coords[n]
      return min(euclid((x,y), goal_pt) for goal_pt in goal_pts)
  return h

def euclid(current_coord, goal_coord):
    (x1,y1),(x2,y2) = current_coord, goal_coord
    distance = math.hypot(x1-x2, y1-y2)
    print(f"Calculating Euclidean distance between {current_coord} and {goal_coord}: {distance}")
    return distance