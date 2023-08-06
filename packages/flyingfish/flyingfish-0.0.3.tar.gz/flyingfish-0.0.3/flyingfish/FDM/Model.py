import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Model:
    def __init__(
            self,
            nrows: int,
            ncols: int,
            max_iter_time: int,
            dt: float
            ) -> None:
        """Constructor for Model class"""

        # spatial discretizaion
        self.nrows: int = nrows
        self.ncols: int = ncols
        self.dx: int = 1
        self.dy: int = 1

        # temporal discretizaion
        self.max_iter_time: int = max_iter_time
        self.dt: float = dt

        # nan-padded grid
        self.grid = np.full(
            shape=(self.max_iter_time, self.nrows+2, self.ncols+2),
            fill_value=np.nan, dtype=float
            )

        # boundary condition names
        self.bc = np.full(
            shape=(self.nrows+2, self.ncols+2),
            fill_value="x", dtype=str
            )

        # specific storage coefficient [1/L]
        self.s = np.full(
            shape=(nrows+2, ncols+2),
            fill_value=np.nan,
            dtype=float
            )

        # hydraulic conductivity [L/T]
        self.kf_x = np.full(
            shape=(nrows+2, ncols+2),
            fill_value=np.nan,
            dtype=float
            )
        self.kf_y = np.full(
            shape=(nrows+2, ncols+2),
            fill_value=np.nan,
            dtype=float
            )

        # sources and sinks
        self.q = np.full(shape=(nrows+2, ncols+2), fill_value=0.0, dtype=float)

    def check_von_neumann_stability(
            self,
            kf_x_val: float,
            kf_y_val: float,
            s_val: float,
            dt: float,
            ) -> None:
        """
        Check the von Neumann stabiity condition.

        $$Ne = \\frac{k_{f}}{S} \\frac{\\Delta t}{(\\Delta x)^2} $$
        """
        neumann_x: float = kf_x_val/s_val * dt/(self.dx**2)
        neumann_y: float = kf_y_val/s_val * dt/(self.dy**2)

        print("\nVon Neumann stability stability criteria (x) = ", neumann_x)
        print("Von Neumann stability stability criteria (y) = ", neumann_y)
        if neumann_x >= 0.5 or neumann_y >= 0.5:
            print("WARNING: no stability guarantee! Ne >= 0.5")

    def set_initial_condition(self, val: float) -> None:
        """Set initial condition, e.g. initial water level."""
        self.grid[:, 1:-1, 1:-1] = val

    def set_homgen_s(self, s_val: float) -> None:
        """Set a homogenous specific storage coefficient."""
        self.s[1:-1, 1:-1] = s_val

    def set_homogen_kf_x(self, kf_x_val: float) -> None:
        """Set a homogenous hydraulic conductivity in x direction."""
        self.kf_x[1:-1, 1:-1] = kf_x_val

    def set_homogen_kf_y(self, kf_y_val: float) -> None:
        """Set a homogenous hydraulic conductivity in y direction."""
        self.kf_y[1:-1, 1:-1] = kf_y_val

    def add_source_sink(
            self,
            loc_list: list[tuple],
            val: float
            ) -> None:
        """Set location and flow rates of a source or sink."""
        for (i, j) in loc_list:
            self.q[i, j] = val

    def add_dirichlet_bc(
            self,
            loc_list: list[tuple],
            val: float
            ) -> None:
        """Set location and groundwater head of a Dirichlet BC (BC I)."""
        for (i, j) in loc_list:
            self.bc[i, j] = "D"
            for t in range(self.max_iter_time):
                self.grid[t, i, j] = val

    def add_neumann_bc(
            self,
            loc_list: list[tuple],
            val: float
            ) -> None:
        """Set location and flow rates of a Neumann BC (BC II)"""
        for (i, j) in loc_list:
            self.bc[i, j] = "N"
            for t in range(self.max_iter_time):
                self.grid[t, i, j] = val

    def __plotheatmap(self, u_t: np.ndarray, t: int):
        """Plot heatmap within GIF."""
        plt.clf()
        plt.title(f"t={t*self.dt:.3f}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.pcolormesh(u_t, cmap=plt.cm.jet, vmin=0, vmax=100)
        plt.colorbar()
        return plt

    def __plot3d(self, u_t: np.ndarray, t: int):
        """Plot 3D surface plot within GIF."""
        plt.clf()
        ax = plt.axes(projection='3d')
        ax.view_init(azim=330, elev=15)
        X, Y = np.meshgrid(
            np.arange(1, self.ncols+1, 1),
            np.arange(1, self.nrows+1, 1)
            )
        ax.plot_surface(
            X, Y,
            u_t[1:-1, 1:-1],
            rstride=1,
            cstride=1,
            cmap='jet',
            vmin=0,
            vmax=100,
            edgecolor='none'
            )
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('water level')
        ax.set_zlim([0, 100])
        plt.title(f"timestep {t}")
        plt.grid(color="gray", alpha=0.2)
        plt.tight_layout()
        return plt

    def __animate(self, t: int) -> None:
        """Pass grid to plotting function."""
        self.__plot3d(self.grid[t], t)

    def get_neighbors(self, t, i, j) -> tuple[float, float, float, float]:
        """Get values of four neighbours."""
        above: float = self.grid[t, i+1, j]
        below: float = self.grid[t, i-1, j]
        left: float = self.grid[t, i, j-1]
        right: float = self.grid[t, i, j+1]
        return above, below, left, right

    def run_simulation(self, plotting: bool, fn: str) -> None:
        """Run simulation and plot result as GIF."""
        start_time = time.time()
        print("\nStart...")

        for t in range(0, self.max_iter_time-1, 1):
            if t % 20 == 0:
                print(f"\tt={t}")

            for i in range(1, self.grid.shape[1]-1, self.dx):
                for j in range(1, self.grid.shape[2]-1, self.dx):

                    # current timestep
                    u_t = self.grid[t][i][j]

                    # sources and sinks
                    sources_sinks = self.dt/self.s[i][j] * self.q[i][j]

                    # central difference in x and y direction
                    if self.bc[i-1, j] == "N":
                        flow = self.grid[t, i-1, j]
                        new = \
                            self.grid[t][i][j] \
                            + (flow*self.dx)/(self.dy*self.kf_x[i][j])
                        central_y = \
                            self.kf_x[i][j]/self.s[i][j] \
                            * self.dt/(self.dx**2) \
                            * (
                                self.grid[t][i+1][j]
                                - 2*self.grid[t][i][j]
                                + new
                                )

                    elif self.bc[i+1, j] == "N":
                        flow = self.grid[t, i+1, j]
                        new = \
                            self.grid[t][i][j] \
                            + (flow*self.dx)/(self.dy*self.kf_x[i][j])
                        central_y = \
                            self.kf_x[i][j]/self.s[i][j] \
                            * self.dt/(self.dx**2) \
                            * (
                                new
                                - 2*self.grid[t][i][j]
                                + self.grid[t][i-1][j]
                                )

                    else:
                        central_y = \
                            self.kf_x[i][j]/self.s[i][j] \
                            * self.dt/(self.dx**2) \
                            * (
                                self.grid[t][i+1][j]
                                - 2*self.grid[t][i][j]
                                + self.grid[t][i-1][j]
                                )

                    central_x = \
                        self.kf_y[i][j]/self.s[i][j] \
                        * self.dt/(self.dy**2) \
                        * (
                            self.grid[t][i][j+1]
                            - 2*self.grid[t][i][j]
                            + self.grid[t][i][j-1]
                            )

                    # new timestep
                    self.grid[t + 1, i, j] = u_t + \
                        sources_sinks + central_x + central_y

        if plotting:
            print("Animate...")
            anim = animation.FuncAnimation(
                plt.figure(),
                self.__animate,
                interval=1,
                frames=self.max_iter_time,
                repeat=False
                )
            anim.save(fn)
            plt.close()
        else:
            pass

        print(f"Done! Runtime={round((time.time()-start_time)/60, 3)} min")
