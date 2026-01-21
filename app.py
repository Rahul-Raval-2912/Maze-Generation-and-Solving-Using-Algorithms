# maze generator and solver with animated visualization
# by vemacitrind
# version: 1.0.0

import tkinter as tk
from tkinter import ttk
import random
import heapq

# config
ROWS = 61
COLS = 81
CELL_SIZE = 14

COLORS = {
    "bg": "#14001F",          
    "wall": "#2A003B",        
    "path": "#F2E9FF",        
    "visited": "#8E6BBF",     
    "current": "#FF4FD8",     
    "start": "#17F707",       
    "end": "#E22B2B",         
    "solution": "#B22222",    
    "solution_done": "#FF1A1A" 
}

# main
class MazeApp:
    def __init__(self, root):
        self.root = root
        root.title("Maze Generator & Solver")
        root.configure(bg=COLORS["bg"])

        self.start = (1, 1)
        self.end = (ROWS - 2, COLS - 2)

        self.animating = False
        self.generator = None
        self.blinking = False
        self.blink_state = True

        self.visited = set()
        self.path = []
        self.current = None
        self.solved = False

        self.create_ui()
        self.reset_maze()

    # UI
    def create_ui(self):
        top = tk.Frame(self.root, bg=COLORS["bg"])
        top.pack(pady=5)

        self.gen_var = tk.StringVar(value="Recursive Backtracking")
        ttk.Combobox(
            top, textvariable=self.gen_var, width=22,
            values=["Recursive Backtracking", "Prim", "Wilson"]
        ).grid(row=0, column=0, padx=5)

        tk.Button(top, text="Generate", command=self.generate).grid(row=0, column=1, padx=5)

        self.solve_var = tk.StringVar(value="Dijkstra")
        ttk.Combobox(
            top, textvariable=self.solve_var, width=22,
            values=["Wall Follower", "Dijkstra", "A*"]
        ).grid(row=0, column=2, padx=5)

        tk.Button(top, text="Solve", command=self.solve).grid(row=0, column=3, padx=5)

        self.speed = tk.IntVar(value=80)
        tk.Scale(top, from_=1, to=200, variable=self.speed,
                 orient="horizontal", label="Speed").grid(row=0, column=4, padx=10)

        self.status = tk.Label(
            self.root, text="", fg="white", bg=COLORS["bg"],
            font=("Arial", 12, "bold")
        )
        self.status.pack()

        self.canvas = tk.Canvas(
            self.root,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg=COLORS["path"]
        )
        self.canvas.pack(pady=10)

    # maze
    def reset_maze(self):
        self.maze = [[1] * COLS for _ in range(ROWS)]
        for r in range(1, ROWS, 2):
            for c in range(1, COLS, 2):
                self.maze[r][c] = 0
        self.visited.clear()
        self.path.clear()
        self.solved = False
        self.stop_blink()
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                color = COLORS["wall"] if self.maze[r][c] else COLORS["path"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        for r, c in self.visited:
            self.paint(r, c, COLORS["visited"])

        if self.current:
            self.paint(*self.current, COLORS["current"])

        sol_color = COLORS["solution_done"] if self.solved else COLORS["solution"]
        for r, c in self.path:
            self.paint(r, c, sol_color)

        self.paint(*self.start, COLORS["start"])
        self.paint(*self.end, COLORS["end"])

    def paint(self, r, c, color):
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    # blinking text
    def blink(self, text):
        self.blinking = True
        self.status.config(text=text)
        self._blink_step()

    def _blink_step(self):
        if not self.blinking:
            return
        self.blink_state = not self.blink_state
        self.status.config(fg="white" if self.blink_state else COLORS["bg"])
        self.root.after(400, self._blink_step)

    def stop_blink(self):
        self.blinking = False
        self.status.config(text="", fg="white")

    # animation eng.
    def animate(self):
        try:
            if self.speed.get() >= 190:
                while True:
                    self.current = next(self.generator)
            else:
                for _ in range(self.speed.get() // 20):
                    self.current = next(self.generator)

            self.draw()
            self.root.after(1, self.animate)

        except StopIteration:
            self.animating = False
            self.current = None
            self.draw()


    # generation
    def generate(self):
        if self.animating:
            return
        self.reset_maze()

        algo = self.gen_var.get()
        if algo == "Recursive Backtracking":
            self.generator = self.dfs_gen()
        elif algo == "Prim":
            self.generator = self.prim_gen()
        else:
            self.generator = self.wilson_gen()

        self.animating = True
        self.animate()
        self.blink("Maze Generated")

    def dfs_gen(self):
        stack = [self.start]
        self.visited.add(self.start)
        while stack:
            r, c = stack[-1]
            yield (r, c)
            neighbors = []
            for dr, dc in [(0,2),(2,0),(0,-2),(-2,0)]:
                nr, nc = r+dr, c+dc
                if 1 <= nr < ROWS-1 and 1 <= nc < COLS-1 and (nr,nc) not in self.visited:
                    neighbors.append((nr,nc))
            if neighbors:
                nr, nc = random.choice(neighbors)
                self.maze[(r+nr)//2][(c+nc)//2] = 0
                self.visited.add((nr,nc))
                stack.append((nr,nc))
            else:
                stack.pop()

    def prim_gen(self):
        start = self.start
        self.visited.add(start)
        walls = []
        r, c = start
        for dr,dc in [(0,2),(2,0),(0,-2),(-2,0)]:
            walls.append((r,c,r+dr,c+dc))
        while walls:
            r,c,nr,nc = random.choice(walls)
            walls.remove((r,c,nr,nc))
            if 1 <= nr < ROWS-1 and 1 <= nc < COLS-1 and (nr,nc) not in self.visited:
                self.visited.add((nr,nc))
                self.maze[(r+nr)//2][(c+nc)//2] = 0
                yield (nr,nc)
                for dr,dc in [(0,2),(2,0),(0,-2),(-2,0)]:
                    walls.append((nr,nc,nr+dr,nc+dc))

    def wilson_gen(self):
        cells = [(r,c) for r in range(1,ROWS,2) for c in range(1,COLS,2)]
        visited = {random.choice(cells)}

        while len(visited) < len(cells):
            start = random.choice([c for c in cells if c not in visited])
            path = {start: None}
            cur = start

            while cur not in visited:
                r,c = cur
                nxt = random.choice([(r+dr,c+dc) for dr,dc in [(0,2),(2,0),(0,-2),(-2,0)]
                                     if 1 <= r+dr < ROWS-1 and 1 <= c+dc < COLS-1])
                path[nxt] = cur
                cur = nxt

            while cur in path:
                prev = path[cur]
                if prev:
                    self.maze[(cur[0]+prev[0])//2][(cur[1]+prev[1])//2] = 0
                visited.add(cur)
                yield cur
                cur = prev

    # solving
    def solve(self):
        if self.animating:
            return
        self.visited.clear()
        self.path.clear()
        self.solved = False

        algo = self.solve_var.get()
        if algo == "Wall Follower":
            self.generator = self.wall_follower_gen()
        elif algo == "A*":
            self.generator = self.astar_gen()
        else:
            self.generator = self.dijkstra_gen()

        self.animating = True
        self.animate()
        self.blink("Path Found")

    def neighbors(self, r, c):
        for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr,nc = r+dr,c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and self.maze[nr][nc]==0:
                yield (nr,nc)

    def wall_follower_gen(self):
        cur = self.start
        path = [cur]
        while cur != self.end:
            yield cur
            for n in self.neighbors(*cur):
                if n not in path:
                    cur = n
                    path.append(cur)
                    break
        self.path = path
        self.solved = True

    def dijkstra_gen(self):
        pq = [(0,self.start)]
        prev = {}
        dist = {self.start:0}
        while pq:
            _,cur = heapq.heappop(pq)
            self.visited.add(cur)
            yield cur
            if cur == self.end:
                break
            for n in self.neighbors(*cur):
                nd = dist[cur]+1
                if n not in dist or nd < dist[n]:
                    dist[n] = nd
                    prev[n] = cur
                    heapq.heappush(pq,(nd,n))
        cur = self.end
        while cur in prev:
            self.path.append(cur)
            cur = prev[cur]
        self.path.append(self.start)
        self.solved = True

    def astar_gen(self):
        h = lambda a,b: abs(a[0]-b[0]) + abs(a[1]-b[1])
        pq = [(h(self.start,self.end), 0, self.start)]
        came = {}
        g = {self.start: 0}

        while pq:
            _,_,cur = heapq.heappop(pq)

            if cur in self.visited:
                continue

            self.visited.add(cur)
            yield cur

            if cur == self.end:
                break

            for n in self.neighbors(*cur):
                tg = g[cur] + 1
                if n not in g or tg < g[n]:
                    g[n] = tg
                    came[n] = cur
                    heapq.heappush(
                        pq,
                        (tg + h(n, self.end), tg, n)
                    )

            self.path.clear()
            p = cur
            while p in came:
                self.path.append(p)
                p = came[p]

        self.path.clear()
        cur = self.end
        while cur in came:
            self.path.append(cur)
            cur = came[cur]
        self.path.append(self.start)
        self.solved = True



# run
if __name__ == "__main__":
    root = tk.Tk()
    MazeApp(root)
    root.mainloop()
