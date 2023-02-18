library(ggplot2)
library(scales)
library(ggpubr)
theme_set(theme_classic())

  
# Data Preparation
prep_data = function(df){
  # Select the general categories
  d = df[as.numeric(df$Commodity.Code) < 100, c('Year', 'Partner', 'Commodity.Code', 'Commodity', 'Trade.Value..US..')]
 
  # Select the trades only with World
  d = d[d$Partner == 'World',]
  
  # Drop NA
  d = d[complete.cases(d),]
  
  # Choose only the top 10 categories
  d = d[d$Commodity.Code %in% codes,]
  d$`Trade.Value..US..` = round(d$`Trade.Value..US..`/10^9, 2)
  
  return(d)
}


# Perform the slope chart
plot_slope = function(df){
  colnames(df) <- c("Commodity", "2016", "2020")
  left_label <- paste(df$Commodity, round(df$`2016`),sep=", ")
  right_label <- paste(df$Commodity, round(df$`2020`),sep=", ")
  df$class <- ifelse((df$`2020` - df$`2016`) < 0, "red", "green")
  
  # Plot
  p <- ggplot(df) + geom_segment(aes(x=1, xend=2, y=`2016`, yend=`2020`, col=class), size=.75, show.legend=F) + 
    geom_vline(xintercept=1, linetype="dashed", size=.1) + 
    geom_vline(xintercept=2, linetype="dashed", size=.1) +
    scale_color_manual(labels = c("Up", "Down"), 
                       values = c("green"="#00ba38", "red"="#f8766d")) +  # color of lines
    labs(x="Year", y="Trade Value (US$ billion)") +  # Axis labels
    xlim(-0.7, 3.7) + ylim(0.99*(min(df$`2016`, df$`2020`)),(1.05*(max(df$`2016`, df$`2020`))))  # X and Y axis limits
    # xlim(-0.25, 3.25)
  
  # Add texts
  p <- p + geom_text(label=left_label, y=df$`2016`, x=rep(1, NROW(df)), hjust=1.1, size=2.7)
  p <- p + geom_text(label=right_label, y=df$`2020`, x=rep(2, NROW(df)), hjust=-0.1, size=2.7)
  p <- p + geom_text(label="2016", x=1, y=1.05*(max(df$`2016`, df$`2020`)), hjust=1.2, size=5)  # title
  p <- p + geom_text(label="2020", x=2, y=1.05*(max(df$`2016`, df$`2020`)), hjust=-0.1, size=5)  # title
  
  # Minify theme
  p + theme(panel.background = element_blank(), 
            panel.grid = element_blank(),
            axis.ticks = element_blank(),
            axis.text.x = element_blank(),
            panel.border = element_blank(),
            plot.margin = unit(c(1,2,1,2), "cm"))
  
}

# Read the datasets
im16 <- read.csv("proj_data/USA_ALL_import_2016_allproduct.csv")
im20 <- read.csv("proj_data/USA_ALL_import_2020_allproduct.csv")
ex16 <- read.csv("proj_data/USA_ALL_export_2016_allproduct.csv")
ex20 <- read.csv("proj_data/USA_ALL_export_2020_allproduct.csv")

# Choose a subset from top 10 categories based on the previous plot
im_codes = c('27', '30', '39', '71', '84', '85', '87', '90', '94', '99')
ex_codes = c('27', '30', '39', '71', '84', '85', '87', '88', '90', '99')
codes = c('27', '30', 
          #'39', 
          '71', '84', '85', '87', '88', '90'
          #'94'
          )
texts = c('Minerals', 
          'Pharmaceutical Products',
          #'Plastic Articles',
          'Gems and Metals',
          'Nuclear Appliances',
          'Electrical Machinery', 
          'Vehicles', 
          'Aerospace',
          'Optical Apparatus'
          #'Furniture'
          )

# Clean the datasets
d_im_16 = prep_data(im16)
d_im_20 = prep_data(im20)
d_ex_16 = prep_data(ex16)
d_ex_20 = prep_data(ex20)

# Make the new summary dataframes for plotting
df_im = data.frame(texts, d_im_16$Trade.Value..US.., d_im_20$Trade.Value..US..)
df_ex = data.frame(texts, d_ex_16$Trade.Value..US.., d_ex_20$Trade.Value..US..)

# Slope chart
s1 <- plot_slope(df_im)
s2 <- plot_slope(df_ex)

# Plot two figures in one row
ggarrange(s1, s2,
          labels = c("Development of Import Trade Value", "Development of Export Trade Value"),
          ncol = 2, nrow = 1)
