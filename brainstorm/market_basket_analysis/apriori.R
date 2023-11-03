
if (require("languageserver")) {
  require("languageserver")
} else {
  install.packages("languageserver", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

# STEP 1. Install and Load the Required Packages ----
## arules ----
if (require("arules")) {
  require("arules")
} else {
  install.packages("arules", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## arulesViz ----
if (require("arulesViz")) {
  require("arulesViz")
} else {
  install.packages("arulesViz", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## tidyverse ----
if (require("tidyverse")) {
  require("tidyverse")
} else {
  install.packages("tidyverse", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## readxl ----
if (require("readxl")) {
  require("readxl")
} else {
  install.packages("readxl", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## knitr ----
if (require("knitr")) {
  require("knitr")
} else {
  install.packages("knitr", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## ggplot2 ----
if (require("ggplot2")) {
  require("ggplot2")
} else {
  install.packages("ggplot2", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## lubridate ----
if (require("lubridate")) {
  require("lubridate")
} else {
  install.packages("lubridate", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## plyr ----
if (require("plyr")) {
  require("plyr")
} else {
  install.packages("plyr", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## dplyr ----
if (require("dplyr")) {
  require("dplyr")
} else {
  install.packages("dplyr", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## naniar ----
if (require("naniar")) {
  require("naniar")
} else {
  install.packages("naniar", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

## RColorBrewer ----
if (require("RColorBrewer")) {
  require("RColorBrewer")
} else {
  install.packages("RColorBrewer", dependencies = TRUE,
                   repos = "https://cloud.r-project.org")
}

library(arules)
library(arulesViz)
library(tidyverse)
library(readr)
library(ggplot2)
library(knitr)
library(magrittr)
library(dplyr)
library(plyr)

# STEP 2. Load and pre-process the dataset ----

# The "read.transactions" function in the "arules" package is used to read
# transaction data from a file and create a "transactions object".

# The transaction data can be specified in either of the following 2 formats:
sales <- read_csv("data/Updated_sales.csv")
dim(sales)



View(sales)

print(sales)
summary(sales)

# Are there missing values in the dataset?
is_na(sales)



#Rename Fields/Columns
colnames(sales)[1] <- "Order_ID"
colnames(sales)[3] <- "Quantity_Ordered"
colnames(sales)[4] <- "Price_Each"
colnames(sales)[5] <- "Order_Date"

#remove unwanted columns
sales_removed_vars <-
  sales %>% dplyr::select(-Address,-Quantity_Ordered,-Price_Each)

dim(sales_removed_vars)
View(sales_removed_vars)

# Also ensure that the product (name of the product purchased) is recorded
# as categorical data
sales_removed_vars %>% mutate(Product = as.factor(Product))
sales_removed_vars$Date <- as.Date(sales_removed_vars$Order_Date, format="%m/%d/%Y")

View(sales_removed_vars)

str(sales_removed_vars)
dim(sales_removed_vars)
head(sales_removed_vars)

#Split Data
transaction_data <-
  plyr::ddply(sales_removed_vars,
              c("Order_ID", "Date"),
              function(df1) {
                paste(df1$Product, collapse = ",")
              }
  )

View(transaction_data)

#Only remain with products
transaction_data <-
  transaction_data %>%
  dplyr::select("items" = V1)

View(transaction_data)

anyNA(transaction_data)

## Save the transactions in CSV format ----
write.csv(transaction_data,
          "data/transactions_basket_format.csv",
          quote = FALSE, row.names = FALSE)

## Read the transactions from the CSV file ----
# We can now, finally, read the baskey format transaction data as a
# transaction object.

tr <-
  read.transactions("data/transactions_basket_format.csv",
                    format = "basket",
                    header = TRUE,
                    rm.duplicates = TRUE,
                    sep = ","
  )

print(tr)
summary(tr)

# STEP 2. Basic EDA ----
# Create an item frequency plot for the top  items 10
itemFrequencyPlot(tr, topN = 10, type = "absolute",
                  col = brewer.pal(8, "Pastel2"),
                  main = "Absolute Item Frequency Plot",
                  horiz = TRUE,
                  mai = c(1, 1, 1, 1))

# STEP 3. Create the association rules ----
# We can set the minimum support and confidence levels for rules to be
# generated.

association_rules <- apriori(tr, 
                             parameter = list(support = 0.001,
                                              confidence = 0.2,
                                              maxlen = 10))



# STEP 3. Print the association rules ----

summary(association_rules)
inspect(association_rules)
#confidence_threshold <- 0.2

# Filter the association_rules to keep only the rules with confidence above the threshold
#filtered_rules <- subset(association_rules, confidence > confidence_threshold)

# Print summary and inspect the filtered rules
#summary(filtered_rules)
#inspect(filtered_rules)
#plot(filtered_rules)

#association_rules_new <- association_rules[!is.redundant(association_rules)]

#inspect(association_rules_new)


### Remove redundant rules ----
# We can remove the redundant rules as follows:
# Number of rules in the association_rules
subset_rules <-
  which(colSums(is.subset(association_rules,
                          association_rules)) > 1)
#getting the length
num_rules <- length(subset_rules)
length(subset_rules)

# Create a sequence of indexes for rules to be removed (1st, 3rd, 5th, etc.) hence remaining with one of each
indexes_to_remove <- seq(1, num_rules, by = 2)

# Remove the rules at the specified indexes
association_rules_no_reps <- association_rules[-indexes_to_remove, ]

# Print summary and inspect the non-redundant rules
summary(association_rules_no_reps)
inspect(association_rules_no_reps)
plot(association_rules_no_reps)



write(association_rules_no_reps,
      file = "rules/association_rules_based_on_product_name.csv")

# STEP 4. Find specific rules ----
# Which product(s), if bought, result in a customer purchasing
# "Samsung USB Type-C to Type-C"?
USB_C_Charging_Cable <-  
  apriori(tr, parameter = list(supp = 0.001, conf = 0.05),
          appearance = list(default = "lhs",
                            rhs = "Samsung USB Type-C to Type-C"))
inspect(head(USB_C_Charging_Cable))

# Which product(s) are bought if a customer purchases
# "iPhone,Google Phone"?
iPhone_Google_Phone <- # nolint
  apriori(tr, parameter = list(supp = 0.001, conf = 0.05),
          appearance = list(lhs = c("Google Pixel 8 Pro", "iPhone 14 Pro Max"), # nolint
                            default = "rhs"))
inspect(head(iPhone_Google_Phone))

# STEP 5. Visualize the rules ----
# Filter rules with confidence greater than 0.85 or 85%
rules_to_plot <-
  association_rules_no_reps[quality(association_rules_no_reps)$confidence > 0.1] # nolint

#Plot SubRules.
plot(rules_to_plot)
plot(rules_to_plot, method = "two-key plot")

top_rules_to_plot <- head(rules_to_plot, n =10, by = "confidence")
install.packages("visNetwork")
plot(top_rules_to_plot, method = "graph",  engine = "htmlwidget")

saveAsGraph(head(rules_to_plot, n = 1000, by = "lift"),
            file = "graph/association_rules.graphml")


# Filter top 20 rules with highest lift
rules_to_plot_by_lift <- head(rules_to_plot, n = 20, by = "lift")
plot(rules_to_plot_by_lift, method = "paracoord")

plot(top_10_rules_to_plot, method = "grouped")



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


