# R statistical analysis for the landing page A/B test.
#
# Reads the cleaned data, computes a group-level summary with dplyr,
# runs a two-proportion z-test comparing conversion rates, and saves two
# ggplot2 figures to outputs/figures/.
#
# Run from the repository root, e.g.:
#   Rscript r/ab_test.R

library(dplyr)
library(ggplot2)
library(readr)

# ---------------------------------------------------------------------------
# 1. Load cleaned data
# ---------------------------------------------------------------------------

ab_data <- read_csv("data/processed/clean_ab_data.csv", show_col_types = FALSE)

dir.create("outputs/figures", recursive = TRUE, showWarnings = FALSE)

# ---------------------------------------------------------------------------
# 2. Group summary (dplyr)
# ---------------------------------------------------------------------------

group_summary <- ab_data |>
  group_by(group) |>
  summarise(
    users = n(),
    conversions = sum(converted),
    conversion_rate = round(conversions / users, 4),
    .groups = "drop"
  )

cat("Group summary:\n")
print(group_summary)


# ---------------------------------------------------------------------------
# 3. Two-proportion z-test
# ---------------------------------------------------------------------------

control_row <- group_summary |> filter(group == "control")
treatment_row <- group_summary |> filter(group == "treatment")

test_result <- prop.test(
  x = c(control_row$conversions, treatment_row$conversions),
  n = c(control_row$users, treatment_row$users)
)

absolute_lift <- treatment_row$conversion_rate - control_row$conversion_rate
relative_lift <- absolute_lift / control_row$conversion_rate

cat("\nAbsolute lift (treatment - control):", round(absolute_lift, 4), "\n")
cat("Relative lift:", round(relative_lift * 100, 2), "%\n")
cat("95% CI for the difference in proportions:",
    round(test_result$conf.int[1], 4), "to", 
    round(test_result$conf.int[2], 4), "\n")
cat("p-value:", signif(test_result$p.value, 4), "\n")

# ---------------------------------------------------------------------------
# 4. Figure 1: conversion rate by group (bar chart)
# ---------------------------------------------------------------------------

fig1 <- ggplot(group_summary, aes(x = group, y = conversion_rate, fill = group)) +
  geom_col(width = 0.6) +
  geom_text(aes(label = scales::percent(conversion_rate, accuracy = 0.1)),
            vjust = -0.5) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
  labs(
    title = "Conversion Rate by Group",
    x = "Group",
    y = "Conversion Rate"
  ) +
  theme_minimal() +
  theme(legend.position = "none")
 
ggsave("outputs/figures/conversion_rate_by_group.png", plot = fig1,
       width = 6, height = 4, dpi = 150)

# ---------------------------------------------------------------------------
# 5. Figure 2: daily conversion rate trend by group (line chart)
# ---------------------------------------------------------------------------
daily_summary <- ab_data %>%
  group_by(experiment_date, group) %>%
  summarise(
    users = n(),
    conversions = sum(converted),
    conversion_rate = conversions / users,
    .groups = "drop"
  )
 
fig2 <- ggplot(daily_summary, aes(x = experiment_date, y = conversion_rate, color = group)) +
  geom_line(linewidth = 1) +
  geom_point(size = 1.5) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
  labs(
    title = "Daily Conversion Rate by Group",
    x = "Date",
    y = "Conversion Rate",
    color = "Group"
  ) +
  theme_minimal()
 
ggsave("outputs/figures/daily_conversion_trend.png", plot = fig2,
       width = 8, height = 4.5, dpi = 150)
 
cat("\nSaved figures to outputs/figures/:\n")
cat(" - conversion_rate_by_group.png\n")
cat(" - daily_conversion_trend.png\n")
 