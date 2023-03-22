base_path <- "../data/island-data-bottle-round-1/"

prices_round_1_day_neg2 <- read.csv(paste(base_path, "prices_round_1_day_-2.csv", sep=""))
prices_round_1_day_neg1 <- read.csv(paste(base_path, "prices_round_1_day_-1.csv", sep=""))
prices_round_1_day_0 <- read.csv(paste(base_path, "prices_round_1_day_0.csv", sep=""))

trades_round_1_day_neg2 <- read.csv(paste(base_path, "/trades_round_1_day_-2_nn.csv", sep=""))
trades_round_1_day_neg1 <- read.csv(paste(base_path, "/trades_round_1_day_-1_nn.csv", sep=""))
trades_round_1_day_0 <- read.csv(paste(base_path, "/trades_round_1_day_0_nn.csv", sep=""))