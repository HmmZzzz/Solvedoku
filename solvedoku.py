import tkinter as tk
from tkinter import messagebox
import time
import copy
import tracemalloc


class SudokuAlgorithm:
    def __init__(self):
        self.steps = 0

    def is_valid(self, board, row, col, num):
        for x in range(9):
            if board[row][x] == num:
                return False
        for x in range(9):
            if board[x][col] == num:
                return False
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True

    #a. BLIND SEARCH DFS
    def solve_blind(self, board, update_ui_callback):
        self.steps = 0
        success = self._solve_blind(board, update_ui_callback)
        return self.steps, success

    def _solve_blind(self, board, update_ui_callback):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            self.steps += 1
                            update_ui_callback(row, col, num, self.steps)

                            if self._solve_blind(board, update_ui_callback):
                                return True

                            board[row][col] = 0
                            self.steps += 1
                            update_ui_callback(row, col, 0, self.steps)
                    return False
        return True

    #b. DFS + HEURISTIC SEARCH
    def solve_heuristic(self, board, update_ui_callback):
        self.steps = 0
        success = self._solve_heuristic(board, update_ui_callback)
        return self.steps, success

    def _find_mrv_cell(self, board):
        min_options = 10
        best_cell = None
        best_options = []
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    options = [num for num in range(1, 10) if self.is_valid(board, row, col, num)]
                    if len(options) < min_options:
                        min_options = len(options)
                        best_cell = (row, col)
                        best_options = options
        return best_cell, best_options

    def _solve_heuristic(self, board, update_ui_callback):
        cell_info = self._find_mrv_cell(board)
        if not cell_info[0]:
            return True

        row, col = cell_info[0]
        options = cell_info[1]

        for num in options:
            board[row][col] = num
            self.steps += 1
            update_ui_callback(row, col, num, self.steps)

            if self._solve_heuristic(board, update_ui_callback):
                return True

            board[row][col] = 0
            self.steps += 1
            update_ui_callback(row, col, 0, self.steps)

        return False


class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solvedoku")
        self.root.geometry("450x700")
        self.root.configure(bg="#f0f0f0")
        self.logic = SudokuAlgorithm()
        self.cells = {}
        self.last_original_board = None
        self.is_solving = False
        self.create_ui()
        self.clear_board()
        self.start_time = 0

    def create_ui(self):
        grid_frame = tk.Frame(self.root, bg="black", bd=2)
        grid_frame.pack(pady=20)

        for row in range(9):
            for col in range(9):
                pady = (1, 3) if row % 3 == 2 and row != 8 else (1, 1)
                padx = (1, 3) if col % 3 == 2 and col != 8 else (1, 1)
                if row == 0: pady = (3, 1)
                if col == 0: padx = (3, 1)

                cell_frame = tk.Frame(grid_frame, bg="black")
                cell_frame.grid(row=row, column=col, padx=padx, pady=pady)

                entry = tk.Entry(cell_frame, width=2, font=("Roboto", 24, "bold"), justify="center", bd=0, fg="blue", bg="white")
                entry.pack(ipady=5)
                self.cells[(row, col)] = entry

        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=5)

        self.reset_btn = tk.Button(btn_frame, text="Reset", font=("Roboto", 10, "bold"), bg="grey", fg="white", width=14, command=self.reset_board)
        
        self.reset_btn.grid(row=0, column=0, padx=5, pady=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear all", font=("Roboto", 10, "bold"), bg="#f44336", fg="white", width=14, command=self.clear_board)
        
        self.clear_btn.grid(row=0, column=1, padx=5, pady=5)

        self.blind_btn = tk.Button(btn_frame, text="Blind Search", font=("Roboto", 10, "bold"), bg="#2196F3", fg="white", width=14, command=self.run_blind_search)
        
        self.blind_btn.grid(row=1, column=0, padx=5, pady=5)

        self.heuristic_btn = tk.Button(btn_frame, text="Heuristic Search", font=("Roboto", 10, "bold"), bg="#FF9800", fg="white", width=14, command=self.run_heuristic_search)
        
        self.heuristic_btn.grid(row=1, column=1, padx=5, pady=5)

        #Display step
        self.status_label = tk.Label(self.root, text="Please enter a Sudoku puzzle and choose a solving method.", font=("Roboto", 10, "bold"), bg="#f0f0f0")
        self.status_label.pack(pady=2)

        #Display memory usage
        self.memory_label = tk.Label(self.root, text="Memory usage: 0.00 KB", font=("Roboto", 10, "bold"), bg="#f0f0f0")
        self.memory_label.pack(pady=2)

        #Display time taken
        self.time_label = tk.Label(self.root, text="Time taken: 0.00s", font=("Roboto", 10, "bold"), bg="#f0f0f0")
        self.time_label.pack(pady=2)



    def toggle_buttons(self, state):
        self.reset_btn.config(state=state)
        self.clear_btn.config(state=state)
        self.blind_btn.config(state=state)
        self.heuristic_btn.config(state=state)

    def reset_board(self):
        if self.is_solving: return
        if self.last_original_board is None:
            self.status_label.config(text="There is no solution to delete it yet")
            return

        for row in range(9):
            for col in range(9):
                self.cells[(row, col)].config(state="normal", fg="blue")
                self.cells[(row, col)].delete(0, tk.END)
                val = self.last_original_board[row][col]
                if val != 0:
                    self.cells[(row, col)].insert(0, str(val))

        self.status_label.config(text="Solution deleted, original puzzle retained")
        self.memory_label.config(text="Memory usage: 0.00 KB")
        self.time_label.config(text="Time taken: 0.00s")

    def clear_board(self):
        if self.is_solving: return
        self.last_original_board = None
        for row in range(9):
            for col in range(9):
                self.cells[(row, col)].config(state="normal", fg="blue")
                self.cells[(row, col)].delete(0, tk.END)
        self.status_label.config(text="Empty board. Please enter a puzzle")
        self.memory_label.config(text="Memory usage: 0.00 KB")
        self.time_label.config(text="Time taken: 0.00s")

    def get_board_from_ui(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for row in range(9):
            for col in range(9):
                val = self.cells[(row, col)].get().strip()
                if val.isdigit() and 1 <= int(val) <= 9:
                    board[row][col] = int(val)
                elif val != "":
                    messagebox.showerror("Error", "Only numbers from 1 to 9 are allowed!")
                    return None
        return board

    def update_single_cell_ui(self, row, col, val, current_step):
        self.cells[(row, col)].config(state="normal")
        self.cells[(row, col)].delete(0, tk.END)

        if val != 0:
            self.cells[(row, col)].insert(0, str(val))
            self.cells[(row, col)].config(fg="black")

        self.status_label.config(text=f"Solving... Step: {current_step}")

        #Update memory usage info (real time)
        current_mem, _ = tracemalloc.get_traced_memory()
        self.memory_label.config(text=f"Memory usage: {current_mem / 1024:.2f} KB")

        # Update time taken info (real time)
        elapsed_time = time.time() - self.start_time
        self.time_label.config(text=f"Time elapsed: {elapsed_time:.5f}s")

        self.root.update()

        #change here to adjust the speed of the UI updates (for demonstration purposes)
        time.sleep(0)

    def lock_board_after_solve(self, original_board):
        for row in range(9):
            for col in range(9):
                if original_board[row][col] != 0:
                    self.cells[(row, col)].config(disabledforeground="blue", disabledbackground="white")
                else:
                    self.cells[(row, col)].config(disabledforeground="black", disabledbackground="white")
                self.cells[(row, col)].config(state="disabled")

    def run_blind_search(self):
        if self.is_solving: return
        original_board = self.get_board_from_ui()
        if original_board is None: return

        self.last_original_board = copy.deepcopy(original_board)
        solve_board = copy.deepcopy(original_board)

        self.is_solving = True
        self.toggle_buttons("disabled")

        # Start tracking memory usage
        tracemalloc.start()
        #Start tracking time
        self.start_time = time.time()

        steps, success = self.logic.solve_blind(solve_board, self.update_single_cell_ui)

        # Get the peak memory usage after solving and stop tracking
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        # Get total time taken
        total_time = time.time() - self.start_time

        if success:
            self.lock_board_after_solve(original_board)
            self.status_label.config(text=f"Blind Search successful! (Total steps: {steps})")
        else:
            self.status_label.config(text=f"No solution found! (Tried {steps} steps)")

        self.memory_label.config(text=f"Peak memory usage: {peak_mem / 1024:.2f} KB")
        self.time_label.config(text=f"Total time: {total_time:.5f}s")

        self.is_solving = False
        self.toggle_buttons("normal")

    def run_heuristic_search(self):
        if self.is_solving: return
        original_board = self.get_board_from_ui()
        if original_board is None: return

        self.last_original_board = copy.deepcopy(original_board)
        solve_board = copy.deepcopy(original_board)

        self.is_solving = True
        self.toggle_buttons("disabled")

        # Statt tracking memory usage
        tracemalloc.start()
        #Start tracking time
        self.start_time = time.time()

        steps, success = self.logic.solve_heuristic(solve_board, self.update_single_cell_ui)

        # Get the peak memory usage after solving and stop tracking
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Get total time taken
        total_time = time.time() - self.start_time

        if success:
            self.lock_board_after_solve(original_board)
            self.status_label.config(text=f"Heuristic Search successful! (Total steps: {steps})")
        else:
            self.status_label.config(text=f"No solution found! (Tried {steps} steps)")

        self.memory_label.config(text=f"Peak memory usage: {peak_mem / 1024:.2f} KB")

        self.time_label.config(text=f"Total time: {total_time:.5f}s")

        self.is_solving = False
        self.toggle_buttons("normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()