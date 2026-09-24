# paper/code/crossimpl_ref.R -- reference outputs for the cross-implementation
# agreement table (Section "Validation and Correctness").
#
# Computes each method with an independent, established R implementation and
# writes the INPUTS and OUTPUTS to paper/code/crossimpl_ref/ as CSV.  This script
# is run once, manually (R is not part of the paper CI); the CSVs are committed.
# paper/code/crossimpl.py then recomputes the fdars side live against these
# frozen references on every CI run, so any numerical drift in fdars shows up
# as a changed agreement table.
#
# Run from the repository root:
#   Rscript paper/code/crossimpl_ref.R

suppressPackageStartupMessages({
  library(fda.usc)
  library(roahd)
  library(fdasrvf)
  library(fdapace)
})

out <- file.path("paper", "code", "crossimpl_ref")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
w <- function(x, name) write.csv(x, file.path(out, name), row.names = FALSE)

# ---------------------------------------------------------------------------
# Berkeley growth heights (93 children x 31 ages), same CSV fdars ships.
# ---------------------------------------------------------------------------
g <- read.csv(file.path("docs", "data", "growth.csv"))
ages <- g$age
X <- t(as.matrix(g[, -1]))                  # rows = children, cols = ages
fd <- fdata(X, argvals = ages)

# 1. Fraiman-Muniz depth (fda.usc), unscaled.
w(data.frame(fm = depth.FM(fd, scale = FALSE)$dep), "fm_depth.csv")

# 2. Modified band depth (roahd).
w(data.frame(mbd = MBD(X)), "mbd.csv")

# 3. FPCA (fda.usc::fdata2pc): singular values and first 4 eigenfunctions.
pc <- fdata2pc(fd, ncomp = 4)
w(data.frame(d = pc$d), "fpca_d.csv")
w(as.data.frame(t(pc$rotation$data[1:4, , drop = FALSE])), "fpca_rotation.csv")

# 4. L2 distance matrix (fda.usc::metric.lp).
w(as.data.frame(metric.lp(fd, lp = 2)), "l2_dist.csv")

# ---------------------------------------------------------------------------
# 5. Elastic Karcher mean (fdasrvf) on synthetic phase-varying bumps.
# ---------------------------------------------------------------------------
set.seed(20260924)
tt <- seq(0, 1, length.out = 101)
n <- 20
shift <- runif(n, -0.12, 0.12)
amp <- runif(n, 0.8, 1.2)
B <- t(sapply(seq_len(n), function(i) amp[i] * exp(-((tt - 0.5 - shift[i]) / 0.08)^2)))
w(as.data.frame(B), "karcher_input.csv")
tw <- time_warping(t(B), tt, lambda = 0, max_iter = 20L)
w(data.frame(t = tt, fmean = as.numeric(tw$fmean)), "karcher_mean.csv")

# ---------------------------------------------------------------------------
# 6. PACE sparse FPCA (fdapace) on synthetic sparse trajectories.
# ---------------------------------------------------------------------------
set.seed(20260925)
ns <- 120
Ly <- vector("list", ns); Lt <- vector("list", ns)
long <- data.frame()
for (i in seq_len(ns)) {
  m <- sample(4:8, 1)
  ti <- sort(runif(m))
  xi1 <- rnorm(1, sd = 2); xi2 <- rnorm(1, sd = 1)
  yi <- 2 * ti + xi1 * sqrt(2) * sin(pi * ti) + xi2 * sqrt(2) * cos(pi * ti) +
        rnorm(m, sd = 0.2)
  Ly[[i]] <- yi; Lt[[i]] <- ti
  long <- rbind(long, data.frame(id = i, t = ti, y = yi))
}
w(long, "pace_input.csv")
fp <- FPCA(Ly, Lt, list(dataType = "Sparse", kernel = "gauss",
                        userBwMu = 0.1, userBwCov = 0.1,
                        methodSelectK = 2, nRegGrid = 51))
w(data.frame(t = fp$workGrid, mu = fp$mu, phi1 = fp$phi[, 1],
             phi2 = fp$phi[, 2]), "pace_fit.csv")
w(data.frame(lambda = fp$lambda[1:2]), "pace_lambda.csv")

# ---------------------------------------------------------------------------
# Provenance: package versions used for the committed references.
# ---------------------------------------------------------------------------
pk <- c("fda.usc", "roahd", "fdasrvf", "fdapace")
w(data.frame(package = pk,
             version = sapply(pk, function(p) as.character(packageVersion(p))),
             R = R.version.string), "versions.csv")
cat("wrote", out, "\n")
