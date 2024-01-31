# Thesis Project - Domain-Specific Sentiment Analysis: A Study of Two Parliaments

Repository contains all relevant code (mostly notebooks) and a bit of sample data. See [this repository](https://www.clarin.si/repository/xmlui/handle/11356/1488) for source data, which will be necessary to reproduce results. Other sources are named in the thesis text. Contact for questions. 

## Sentiment Dictionaries

Sentiment dictionaries (named Parlex) for parliamentary speech - available in Bulgarian and Danish.

## Thesis Abstract

In recent years, the availability of parliamentary transcriptions has motivated the use of
Natural Language Processing (NLP) methods for investigating these datasets
quantitatively. One area of study for political scientists has been the expression of
emotion by parliamentary speakers and the factors that influence it. However, there is a
lack of research on non-anglophone legislatures and insufficient validation of existing
sentiment analysis methods. In this study, a technique for creating domain-specific
sentiment lexica with word embeddings is applied to datasets of parliamentary speech
from Bulgaria and Denmark in order to investigate the effects of party status and
proceeding type. By embedding each corpus with Global Vectors (GloVe), manually
produced seed lists of positive and negative words can be expanded using measures of
vector similarity. The resulting lexica, called ParLex DK/BG, are used to score and
compare the two corpora. The sentiment analysis indicates that for both legislatures,
government/coalition status is associated with more positive emotion relative to
opposition or other status, though this is much more pronounced in Denmark. With
regard to proceeding type, there is no consistent cross-national pattern, but proceeding
type does interact with party status. In both countries, sentiment gaps between coalition
and opposition are largest during ministerial questionings, and in the Bulgarian
parliament, the effect of party status is only clearly apparent during questionings and
draft decisions. These differences may reflect the contrast between a more established
(Denmark) and more politically turbulent (Bulgaria) legislature. Confidence in these
results is also moderated by evaluation with a hand-annotated gold standard of speeches.
Correlation between ParLex and manual annotation is 0.40 for Bulgarian and 0.48 for
Danish. ParLex DK is also outperformed by a common general-use lexicon, indicating
that domain-specificity does not offer clear advantages when analyzing parliamentary
speech. Both lexica are made publicly available with suggestions and recommendations
for future work.




