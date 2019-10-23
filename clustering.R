data = read.csv('C:/Users/Administrator/Desktop/clustering_new/clustering_new.csv',header=T)
dim(data)
data <- na.omit(data)
dim(data)
data_nomal <- scale(data[3:34])
data[3:34] = data_nomal
View(data)

library(tidyverse)
library(cluster)
library(factoextra)

# get the distance
head(data)
distance <- get_dist(data[3:34])
fviz_dist(distance, gradient = list(low = "#00AFBB", mid = "white", high = "#FC4E07"))

# determine k
fviz_nbclust(data[3:34],kmeans,method="silhouette")

# k = 3
k3 <- kmeans(data[3:34], centers = 3, nstart = 25)
str(k3)
k3
fviz_cluster(k3, data = data[3:34],geom = 'point',main= "3 clusters")

# k = 10
k10 <- kmeans(data[3:34], centers = 10, nstart = 25)
str(k10)
k10
fviz_cluster(k10, data = data[3:34],geom="text",labelsize=6,show.clust.cent=FALSE,main= "10 clusters")
fviz_cluster(k10, data = data[3:34],geom ='point',main= "10 clusters")

# get the result
library(NbClust)
k10$cluster
write.table(k10$cluster, file = 'C:/Users/Administrator/Desktop/cluster.txt')
