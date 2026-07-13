---
title: "The second New England RLHF Hackers Hackathon"
categories: ["Research Notes"]
author: ['Suraj Anand', 'Chase Blagden', 'Louis Castricato', 'Yeganeh Kordi', 'Francisco Piedrahíta-Vélez', 'Arjun Prakash', 'Logan Riggs', 'Benjamin Spiegel', 'Kevin A. Wang', 'Benjamin Wright', 'Yong Zheng-Xin', 'Max Zuo']
date: 2023-10-13T14:00:00-06:00
draft: False
---


# Introduction

Rekindling the spirit of collaboration, the New England RLHF Hackers (NERH) hosted their second hackathon at Brown University on October 8th, 2023. Stepping up from the success of our inaugural hackathon, this event was fueled by the same enthusiasm but with a fresh purpose: to brainstorm and formulate solutions to a myriad of existing challenges in reinforcement learning from human feedback. The NERH group is mainly comprised of collaborators and contributors from EleutherAI, with several members being integral parts of the Eleuther workforce. In light of our shared vision for a more transparent and inclusive RLHF community, we've decided to unveil our discoveries from the intense brainstorming sessions, no matter how experimental or preliminary they might seem.

For anyone around New England or those willing to journey to Rhode Island, consider this an open invitation to our future hackathons. Every additional perspective amplifies the quality of our collaborative endeavors.

Feel free to connect with us through our NERH Discord: (Kindly ensure you're keen on attending in person before joining.) https://discord.gg/yxC4BrUyBu

For academic referencing, the DOI entry for this blog post can be found at the conclusion.


# Sparse Autoencoders Find Features in Reward Models


Authors: Benjamin Wright, Logan Smith


## Introduction


Sparse Autoencoders (SAE) are a scalable, unsupervised approach which finds linear feature directions that correspond to human interpretable, semantic concepts. We apply this to a reward model (RM) in order to find features that most affect reward (e.g. a cursing feature may cause lower reward on average). It may be the case that the reward model is upweighting/downweighting features that are different than the developers intended, which if found in an SAE, can easily be changed to better fit specification.
  
## Objective


Our goal is to understand the features represented in reward models and how they affect models trained using this reward model. 


## Approach
We learned an SAE on the 10th layer of Pythia-6.9B-RM hosted on by [usvsnsp](https://huggingface.co/usvsnsp/pythia-6.9b-rm-full-hh-rlhf). We then ablate each feature one at a time to see the effect on reward, sorting features by their effect. This then gives us a list of the features that most affect reward, both positively and negatively.


These features can then be analyzed by both:
1. Datapoints that activate this feature - running across a large dataset, we can collect which datapoints cause this feature to activate. We specifically collect datapoints across a range of activations since that gives a more accurate representation of what a feature represents.
2. Effect on reward when removing this feature - we can remove this feature’s activation by effectively zero-ing out the row that represents this feature. We can then see that, when the model can’t represent this concept as usual, how does the RM’s scoring of the text change.


## Results
Early results show that the reward model is strongly tilted towards stronger negative features i.e. detecting features of what NOT to do. Some of these features include politics, fighting, and pregnancy, although no systematic analysis of these features have been done beyond a cursory glance. 


## Future Work
We’d like to give a more systematic analysis of features found in the reward model, including generating text examples which show clear misalignment between the RM’s score and what is initially intended. For example, the RM is intended to be helpful, which isn’t captured by a systematic bias against discussing pregnancy terms. This might be shown by writing two responses to a pregnancy question with the same content value; however, one has clear pregnancy terms and the other euphemisms, where the euphemism one is expected to be higher reward.


## Summary


This work explores the use of SAEs to identify and understand features in a RM. We focused on the 10th layer of the Pythia-6.9B-RM model. Features affecting the RM were isolated by ablating them one by one and observing their impact on reward. We found that the RM strongly emphasizes negative features, such as politics and pregnancy. Future work aims to provide a more systematic analysis to uncover misalignments between intended and actual rewards, particularly in areas where the RM is not capturing the intended helpfulness.

# Synthetic Preference Data using MCTS

Authors: Chase Blagden, Arjun Prakash, Kevin A. Wang

## Introduction
In RLHF a key part of the process is collecting the preference data used to train the reward model. However, gathering this data can be expensive and time consuming. RLAIF attempts to circumvent this by using a LLM to produce completions and then rank the completions itself. To make a set of diverse, synthetic preference data we decide to use Monte Carlo tree search (MCTS) to generate completions.

## Motivation
We hypothesize that having a tree of different possible completions and their rankings for single prompt will provide a richer source of signal to signal for a rewards model and ultimately how it is distilled into a LLM rather than just having a pair of distinct completions for each prompt in a dataset.

## Project Goal:
To create a synthetic preference dataset of prompts with completions by traversing a tree created via MCTS.

## Approach
To test our technique, we first decided to generate using a simpler task rather than just all of natural language on any prompts at first. We decided to use the knapsack problem, since it is simple to formulate as a single player game and easy to verify and make different instances of the problem with varying complexities. We can then use a language model as the policy in MCTS. Once we have a tree, we can traverse it to grab different pairings of completions and use the values of each path from MCTS to label each pair with a reward. 
Once we have this rewards dataset for the knapsack problem, we can then use RL to optimize the policy model. To validate our technique, we should see that the RL-trained policy model should have a higher performance on the knapsack problem - e.g. that it gets a higher fraction of its “knapsack” filled on average. 
As a base case, we will also sample two completions per each instance of a problem, and then compute the values of each of those to form a dataset. If our hypothesis is true, then we should see that the dataset formed via MCTS should give a higher performing model than our base case dataset.

## Future Work
Next, we want to apply to create a synthetic preference dataset for natural language instead. An issue with this domain is that we no longer have an oracle - unlike the knapsack problem - for ranking completions. To circumvent this, we can use another LLM like GPT-4 to rank the quality of a competition to obtain a score for it. We can then use these scores to rank the completions to create the final preference dataset. 

## Summary
Using the RLHF method, we aim to produce synthetic preference data via Monte Carlo tree search (MCTS). We initially test with the knapsack problem, using a language model for MCTS policy. After tree traversal and reward assignment, RL optimization enhances the policy model's performance. Future plans involve adapting this for natural language datasets, leveraging LLMs like GPT-4 for scoring completions without a clear oracle.


# The Pink Elephant Problem in Language Models

Authors: Louis Castricato, Suraj Anand, Yong Zheng-Xin


## Introduction

The psychological "pink elephant" problem highlights the challenge of trying to avoid thinking about something, only to become fixated on it. This concept mirrors issues in language models where networks generate undesirable content even when programmed (i.e. prompted) to avoid it. Drawing from this analogy, our project explores the use of Reinforcement Learning from Artifical Intelligence Feedback (RLAIF) to constrain a language model's outputs, aiming to prevent such unwanted responses and **stick to the desirable content** at the same time. For example, a company may not want its customer service language model to generate responses that include references to competitors when being asked about their competitors. Likewise, it may be critical to prevent language models from generating toxic or dangerous content, or to ensure that certain models remain specialized and don't deviate into unrelated topics.

## Contributions
- Datasets: We curated a dataset of 200K multi-turn conversations on the Pink Elephant problem.

## Objective

Our goal is to leverage RLAIF in order to restrict a language model from generating responses related to specific topics and generate the desirable topics instead.

### Dataset Generation Procedure

1. Topics Generation: We prompted GPT-4 on the topics that are normally mentioned in daily conversations.

2. Pink Elephant Pairs (PEP): Based on the set of topics, we prompted GPT-4 to generate diverse contrastive pairs (which is defined as pairs of terms that differ on certain characteristics but share similar concept) such as "Nike - Adidas" for the topic of sports, "Taj Mahal - Ellora Caves" for travel, and "iOS - Android" for technology. 

3. Pink Conversation Generation: For each pair, create fifty distinct plans outlining how a conversational agent might talk about on the particular topic with the PEP such that the conversation naturally shifts from one term to the other. Then, for each plan, generate a conversational dialogue between a user and an agent. The final output would be like the user starts talking about Nike and asks about Adidas at the end of the conversation.

4. Grey Conversation Generation: Use `autocrit` to generate a critique of the  agent's last utterance in the dialogue that specifies an unwanted reference to pink-elephant term and a revision of the dialogue that removes this unwanted reference and replaces with the desired reference. Now, we would obtain a conversational dialogue between a user and an agent where the user asks about the pink-elephant term but the agent not only refuses to engage, but naturally brings the conversation back to the desired term.





## Progress since last hackathon
- **Data generation pipeline**: Previously, the data generation generated PEP, which makes it difficult to scale up the number of PEP without overlapping or degradation in quality. To overcome this, we introduce a step before PEP generation, which is to generate diverse topics. Then, we generate PEP conditioned on the topics.
- **Critique/Revision**: Previously, we asked the model to regenerate the whole conversation, which can be computationally expensive. Now, we only ask the model to generate (revise) the last turn of the conversation.
- **ST Tensor** - We can obtain computation graph with `ST` tensor that wraps around the string text.
- **async** - Our conversation generation and critique/revision now support `async` operations.


# How to cite

```
@online{nerh_hackathon2_2023,
  title = {The second New England RLHF Hackers Hackathon},
  author = {Suraj Anand and Chase Blagden and Louis Castricato and Yeganeh Kordi and Francisco Piedrahíta-Vélez and Arjun Prakash and Logan Riggs and Benjamin Spiegel and Kevin A. Wang and Benjamin Wright and Yong Zheng-Xin and Max Zuo},
  year = {2023},
  month = {10},
  url = {https://blog.eleuther.ai/nerh_2/},
  note = {Blog post},
}

```
