########### Analysis Compelled Movements Direction Change   #########
### Clara Kuper 2019 ################################################
#####################################################################
### Goals: ##########################################################
### Psychometric Function: % correct responses for goal distance (flight time)
### Sanity check: response times as a function of distance

########## Set wd and co ###########################################
setwd("~/Projects/CompelledMovements/analysis")

data_path <- '../data/'
figure_path <- '../figures/'

########## Import functions and packages ###########################


########## Import Data #############################################
ck01 <- read.table(paste(data_path,'CoMo2ck1.txt', sep = ''), header = TRUE)
des_ck01 <- read.table(paste(data_path,'CoMo2desck1.txt', sep = ''), header = TRUE)


all_resp <- ck01
all_des <- des_ck01

######### Preview Plots ###########################################
## Reaction times as function of distance
plot(all_des$change_loc,all_resp$t_response, ylim=c(-0.0,0.5))

######## Add reverse responses ####################################
for (trial in 1:nrow(all_des)){
  if (all_des$change[trial] == 1){
    if(all_des$direction[trial] == '-'){
    all_des$rev_sign[trial] <- '+'   
    }
    else{
    all_des$rev_sign[trial] <- '-'  
    }
  }
  else {
    if(all_des$direction[trial] == '-'){
      all_des$rev_sign[trial] <- '-'   
    }
    else{
      all_des$rev_sign[trial] <- '+'  
    }
  }
}

for (trial in 1:nrow(all_des)){
  if (all_des$rev_sign[trial] == '-'){
    if(all_resp$response[trial] == 'n'){
      all_resp$correct[trial] <- 0
    }
    if(all_resp$response[trial] == 'v'){
      all_resp$correct[trial] <- 1
    }
  }
  else if (all_des$rev_sign[trial] == '+') {
    if(all_resp$response[trial] == 'n'){
      all_resp$correct[trial] <- 1
    }
    if(all_resp$response[trial] == 'v'){
      all_resp$correct[trial] <- 0
    }
  }
}


#### percent correct as function of reaction time
for (resp in unique(all_resp$correct)){
  id = which(all_resp$correct == resp)
  hist(all_des$change_loc[id]) 
}

timewin = 20
steps = seq(-0.1,0.5,0.05)
start = 0
outmat = matrix(nrow=length(steps), ncol = 2)
all_resp$correct <- as.numeric(all_resp$correct)

for (step in steps){
  idx_time <- which(all_resp$t_response>=start & all_resp$t_response<=step)
  samples <- length(idx_time)
  percentage <- sum(all_resp$correct[idx_time])/samples
  outmat[which(steps == step),1] <- step
  outmat[which(steps == step),2] <- percentage
  start = step
}

plot(outmat[,1],outmat[,2])

#### percent correct as function of goal distance
steps_dis = seq(-2,-9)
start_dis = 0
outmat_dis = matrix(nrow=length(steps_dis), ncol = 2)

for (step in steps_dis){
  idx_time <- which(all_des$change_loc<=start_dis & all_des$change_loc>=step)
  samples <- length(idx_time)
  percentage <- sum(all_resp$correct[idx_time])/samples
  outmat_dis[which(steps_dis == step),1] <- step
  outmat_dis[which(steps_dis == step),2] <- percentage
  start_dis = step
}

plot(outmat_dis[,1],outmat_dis[,2])

#### percent correct as function of processing time
all_resp$ePT <- (all_resp$t_change-all_resp$t_response) * all_des$change

steps_dis = seq(-0.1,1,0.1)
start_dis = -0.2
outmat_dis = matrix(nrow=length(steps_dis), ncol = 2)

for (step in steps_dis){
  idx_time <- which(all_resp$ePT >= start_dis & all_resp$ePT <= step)
  print(idx_time)
  samples <- length(idx_time)
  percentage <- sum(all_resp$correct[idx_time])/samples
  outmat_dis[which(steps_dis == step),1] <- step
  outmat_dis[which(steps_dis == step),2] <- percentage
  start_dis = step
}

plot(outmat_dis[,1],outmat_dis[,2])
