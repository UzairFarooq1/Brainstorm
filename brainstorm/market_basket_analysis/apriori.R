library(arules)
library(arulesViz)
library(tidyverse)
library(readr)
library(ggplot2)
library(knitr)
library(magrittr)
library(dplyr)
library(plyr)
library(tidyverse)

sales <- read_csv("data/Updated_sales.csv")
view(sales)

summary(sales)

sales <- sales[complete.cases(sales), ]





sapply(sales, class)


colnames(sales)[1] <- "Order_ID"
colnames(sales)[3] <- "Quantity_Ordered"
colnames(sales)[4] <- "Price_Each"
colnames(sales)[5] <- "Order_Date"

transactionData <- ddply(sales, c("Order_ID", "Order_Date"),
                         function(df1) paste(df1$Product,
                                             collapse = ","))

transactionData$Order_ID <- NULL
transactionData$Order_Date <- NULL
colnames(transactionData) <- c("Product")

write.csv(transactionData, "data/salesNew.csv", quote = FALSE, row.names = FALSE)

transaction <- read.transactions("data/salesNew.csv", format = "basket", sep = ",")

summary(transaction)

basket_rules <- apriori(transaction, parameter = list(minlen=2, sup = 0.001, conf = 0.05, target="rules"))
print(length(basket_rules))


inspect(basket_rules[1:6])


plot(basket_rules, jitter = 0)

plot(basket_rules, method = "grouped", control = list(k = 5))

plot(basket_rules[1:6], method="graph")

plot(basket_rules[1:6], method="graph")

plot(basket_rules[1:6], method="paracoord")

itemFrequencyPlot(transaction, topN = 10)

basket_rules2 <- apriori(transaction, parameter = list(minlen=3, sup = 0.001, conf = 0.1, target="rules"))

print(length(basket_rules2))

summary(basket_rules2)

inspect(basket_rules2)

plot(basket_rules2, method="graph")

plot(basket_rules2, method="paracoord")

