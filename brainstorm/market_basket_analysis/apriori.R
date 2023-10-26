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

payment_orderitem <- read.csv("data/payment_orderitem.csv", header = TRUE)
store_product <- read.csv("data/store_product.csv", header = TRUE)
store_product$title <- gsub(",", "", store_product$title)

View(payment_orderitem)

# Merge the dataframes together by their shared variables and add argument all.x=T (the default) to ensure all rows are kept from your database containing species.
sales <- payment_orderitem %>%
  left_join(store_product, by = c("product_id" = "id"))
# View the merged data

view(sales)

summary(sales)

sales <- sales[complete.cases(sales), ]

sapply(sales, class)


colnames(sales)[1] <- "Order_ID"
colnames(sales)[3] <- "Quantity_Ordered"
colnames(sales)[4] <- "Price_Each"
colnames(sales)[5] <- "Order_Date"

transactionData <- ddply(sales, c("order_id"),
                         function(df1) paste(df1$title,
                                             collapse = ","))

transactionData$order_id <- NULL
transactionData$Order_Date <- NULL
colnames(transactionData) <- c("title")



write.csv(transactionData, "data/orderitemNew.csv", quote = FALSE, row.names = FALSE)

transaction <- read.transactions("data/orderitemNew.csv", format = "basket", sep = ",")

summary(transaction)
View(transactionData)
basket_rules <- apriori(transaction, parameter = list(minlen=2, sup = 0.001, conf = 0.05, target="rules"))
print(length(basket_rules))


inspect(basket_rules[1:4])


plot(basket_rules, jitter = 0)

plot(basket_rules, method = "grouped", control = list(k = 5))

plot(basket_rules[1:6], method="graph")

plot(basket_rules[1:6], method="graph")

plot(basket_rules[1:6], method="paracoord")

itemFrequencyPlot(transaction, topN = 10)


