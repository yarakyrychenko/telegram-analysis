
#install.packages("librarian")
librarian::shelf(dplyr, ggplot2, ggraph, 
                 rtweet, academictwitteR, quanteda, jsonlite,
                 quanteda.textplots, quanteda.textstats)
lib_startup()

json_file <- "rt_russian_chat.json"
file <- fromJSON(paste(readLines(json_file), collapse=""), flatten=TRUE)

colnames(file)

my_corpus <- quanteda::corpus(file$message)

preprocess <- function(data){
  text <- tolower(data$message)
  text <- stringi::stri_replace_all_regex(text, "#", "")
  toks_tweets <- tokens(text, remove_punct = TRUE, remove_url = TRUE, remove_numbers = TRUE, 
                        remove_symbols = TRUE, split_hyphens = TRUE) %>% 
    tokens_select(pattern = stopwords("ru"), selection = "remove")
    #tokens_keep(keep)
  dfmat_tweets <- dfm(toks_tweets) 
  return(dfmat_tweets)
}

dfmat_tw <- preprocess(file)
tstat_freq <- textstat_frequency(dfmat_tw)
tstat_freq

set.seed(132)
textplot_wordcloud(dfmat_tw, max_words = 150,max_size =10)