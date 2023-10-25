# Load the required libraries
library(arules)
library(arulesViz)

# Load the dataset
data <- read.csv("data/payment_orderitem.csv")

# Convert the dataset into a transaction object
transactions <- as(data, "transactions")

# Mine frequent itemsets using Apriori algorithm
frequent_itemsets <- apriori(transactions, parameter = list(support = 0.01, confidence = 0.5))

# Mine association rules from frequent itemsets
association_rules <- as(frequent_itemsets, "rules")

# Visualize the association rules
plot(association_rules)
