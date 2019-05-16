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
ck05 <- read.table(paste(data_path,'ck5.txt', sep = ''), header = TRUE)
ck07 <- read.table(paste(data_path,'ck7.txt', sep = ''), header = TRUE)
des_ck05 <- read.table(paste(data_path,'desck5.txt', sep = ''),sep = ',', header = TRUE)
des_ck07 <- read.table(paste(data_path,'desck7.txt', sep = ''),sep = ',', header = TRUE)

all_resp <- rbind(ck05,ck07)
all_des <- rbind(des_ck05,des_ck07)

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

plot(all_des$distance,all_resp$correct, ylim=c(-0.0,1))
