### This is the analysis of the Compelled Movements Football task ###
### Clara Kuper 2019 ################################################
#####################################################################
### Goals: ##########################################################
### Psychometric Function: % correct responses for goal distance (flight time)
### Sanity check: response times as a function of distance

########## Set wd and co ###########################################
data_path <- '../data/'
figure_path <- '../figures/'

########## Import functions and packages ###########################


########## Import Data #############################################
ck01 <- read.table(paste(data_path,'ck1.txt', sep = ''), header = TRUE)
des_ck01 <- read.table(paste(data_path,'desck1.txt', sep = ''), header = TRUE)


all_resp <- ck01
all_des <- des_ck01

######### Preview Plots ###########################################
## Reaction times as function of distance
plot(all_des$distance,all_resp$t_response, ylim=c(-0.0,0.5))
for (trial in 1:nrow(all_des)){
  if (all_des$direction[trial] == '-'){
    if(all_resp$response[trial] == 'n'){
      all_resp$correct[trial] <- 0
    }
    if(all_resp$response[trial] == 'v'){
      all_resp$correct[trial] <- 1
    }
  }
  else if (all_des$direction[trial] == '+') {
    if(all_resp$response[trial] == 'n'){
      all_resp$correct[trial] <- 1
    }
    if(all_resp$response[trial] == 'v'){
      all_resp$correct[trial] <- 0
    }
  }
}

for (distance in unique(all_resp$correct)){
  id = which(all_resp$correct == distance)
  hist(all_des$distance[id]) 
}
