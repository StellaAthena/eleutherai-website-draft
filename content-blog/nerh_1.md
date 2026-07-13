---
title: "The first New England RLHF Hackers Hackathon"
categories: ["Research Notes"]
author: ["Suraj Anand", "Stephen Casper", "Louis Castricato", "Arjun Khurana", "Alyssa Loo", "Shukai Ni", "Benjamin Spiegel", "Jiayu Zheng", "Yong Zheng-Xin"]
# description: "We evaluate different fewshot prompts on GPT-3 to see how it changes performance."
date: 2023-09-19T14:00:00-06:00
draft: False
---


# Introduction

Author list is alphabetical by last name. We would like to extend acknowledgements to Delta Christine Hessler and Hailey Schoelkopf.

On September 10, 2023, New England RLHF Hackers (NERH) held a hackathon at Brown University. For this hackathon we came in with one simple goal: to come up with plans to solve varying open problems in reinforcement learning from human feedback. Most members of NERH were contributors and collaborators at EleutherAI, with some of us actually being directly employed by Eleuther. As such, after the conclusion of the first NERH hackathon, we decided it was in the best interests of the RLHF community at large to release our findings of a few hour-long sprints,regardless of how negative they were.

Below are a number of hacks conducted during that late, rainy, summer Sunday. If you are in the New England area or willing to commute to Rhode Island for a day, we’d love for you to join a future hackathon.

Invite to NERH Discord: (Please only join if you are willing to attend in person.) https://discord.gg/yxC4BrUyBu 


If you would like to cite this blog post, we’ve included a DOI entry at the bottom of this page.


# On the Evaluation of Reward Models

Authors: Alyssa Loo

## Introduction

The quality of a learned reward model is typically indirectly evaluated with the qualitative performance of the end-to-end RLHF model. However, the policy optimization process is computationally expensive to run and highly fragile to tune. Under the assumption that the quality of the reward model provides—at least—a lower bound on the performance of the final RLHF model, a method to directly evaluate the reward model would expedite the process of RLHF training.
  
## Objective

This project aims to propose a framework for which reward models may be directly evaluated. The evaluation framework aims to provide useful signal for the tuning of reward models independent of the end-to-end RLHF model.

## Approach

It is difficult to define what constitutes as desired behavior for any specific reward model, given the (i) diversity of human preferences and values; (ii) the diversity of domains to which reward models are applied; and (iii) the tradeoffs between the desired attributes for any reward model—for instance, that a model may at times need to be unhelpful to avoid being harmful.

However, it appears far more straightforward to define what are *undesirable* behaviors for any reward model. It is presumably uncontroversial that we want reward models to penalize answers that are harmful, unhelpful, untruthful, etc. It may be more subjective as to how some negative attributes should be traded off for others—we may prefer a model to be unhelpful than harmful, for instance—but an ideal reward model should be sensitive to the presence of any of these negative attributes. 

With this intuition in mind, our proposed approach is to train an ensemble of classifiers that are each independently sensitive to some undesirable attribute. For instance, a 'harmfulness' classifier will assign a 'harmfulness' score to any given model response, independent of how unhelpful or untruthful the response may have been. We can then relate a reward model's scores as a function of these classifiers' scores. 

This approach aims to serve as a heuristic assessment: a good reward model should assign scores that hold a strong inverse correlation with the scores of these classifiers, and a bad reward model may demonstrate substantial unexplained variance in relation to the classifiers' scores. One benefit of this approach is also that it allows greater interpretability of reward model scores: we may be able to see that a reward model penalizes unthruthfulness more greatly than unhelpfulness, for example. However, this approach does not propose that the scores of these classifiers be themselves the metric to optimize reward.

## Implementation

With the aim of building a proof-of-concept, we are currently building classifiers for the negative attributes of unhelpfulness and harmfulness. We use [Anthropic's HH-RLHF dataset](https://huggingface.co/datasets/Anthropic/hh-rlhf), with 'chosen' responses within each helpfulness/harmfulness split being classified as 1 for that attribute, and 'rejected' responses being classified as 0.

Currently, we have tried training classifiers for 30 epochs with two models (i) RoBERTA and (ii) GPT-2 Small, achieving poor results of ~0.44 for harmfulness and ~0.65 for helpfulness. Building better classifiers is hence the main ongoing work.

Once we have achieved classifiers with good classification accuracy, we aim to fit a hierarchal linear model between scores from the classifier and scores from various sizes of reward models.

## Summary

In this post we propose a heuristic approach to directly evaluating reward models that is domain-agnostic and interpretable. Implementation of a proof-of-concept for the approach is underway.


# A Fact-Based Reward Model for Language Models

Authors: Ben Spiegel, Arjun Khurana, Jiayu Zheng, Shukai Ni 

## Introduction

Traditional Reinforcement Learning from Human Feedback (RLHF) often leans on the abstract notion of human preference to train Large Language Models (LLMs) to be kind, factual, and helpful. While this approach has merits, it's not always effective in optimizing for factual accuracy. Unlike human opinions, facts are not a matter of consensus but are usually grounded in evidence, expert analysis, or logical reasoning. To address this gap, our project introduces a fact-based reward model that leverages reliable online sources and logical inference.

## Project Goal

Our primary aim is to create a reward model that values factual accuracy over mere human preference. We utilize established online databases like Stack Exchange and Wikipedia as trusted sources to guide the model's learning process. By doing so, we aim to minimize the model's chances of generating inaccurate or misleading information.

## Key Components

The reward model is comprised of two main elements:

1. A specialized Large Language Model (LLM) trained for logical reasoning and inference, referred to as the logician LLM.
2. A robust document search API designed to find relevant and trustworthy documents related to the given prompt and completion.

## How It Works

1. For a given prompt and the LLM's completion, the search API fetches 10 relevant documents.
2. The logician LLM then reviews these documents to assess whether the completion is factual or conflicts with the retrieved information.
3. A score between 0 and 1 is assigned as a reward, based on this analysis.

Our hypothesis is that this approach will reduce inaccuracies and improve the factual integrity of the generated text, although we recommend using this model in conjunction with traditional, preference-based models for optimal results.

## Extended Project Scope

We further expanded the project to correct any inaccuracies in the model's responses. Utilizing the trusted documents retrieved, a second LLM rewrites the completion to align it more closely with verified information. This also allows us to generate a dataset in the form of (p, c1, c2), where score(c2) > score(c1), which can be useful for training traditional reward models.

## Summary

Our fact-based reward model diverges from the standard RLHF approach by prioritizing verified information over human preference. It not only enhances the factual accuracy of the model's outputs, but also provides a pathway for correcting misinformation, making it a valuable addition to the realm of LLM training methods.




# The Pink Elephant Problem in Language Models

Authors: Louis Castricato*, Suraj Anand*, Yong Zheng-Xin

## Introduction

The psychological "pink elephant" problem highlights the challenge of trying to avoid thinking about something, only to become fixated on it. This concept mirrors issues in language models where networks generate undesirable content even when programmed (i.e., prompted) to avoid it. Drawing from this analogy, our project explores the use of Reinforcement Learning from Artificial Intelligence Feedback (RLAIF) to constrain a language model's outputs, aiming to prevent such unwanted responses. For example, a company may not want its customer service language model to generate responses that include references to competitors. Likewise, it may be critical to prevent language models from generating toxic or dangerous content or to ensure that certain models remain specialized and don't deviate into unrelated topics.

## Objective

Our goal is to leverage RLAIF to restrict a language model from generating responses related to specific topics—in our case, the topic of Ubuntu.  

## Procedure

1. Generate a diverse list of topics where one could potentially ask a question that would elicit an answer related to Ubuntu.
  
2. For each topic, create five distinct plans outlining how a conversational agent might respond in a manner that includes information about Ubuntu.

3. For each plan, generate a conversational dialogue between a user and an agent. Cut the dialogue at the first agent reference to *Ubuntu* or an *Ubuntu-exclusive service*.  

4. Use [autocrit](https://github.com/CarperAI/autocrit) to generate a critique of the agent's last utterance in the dialogue that specifies an unwanted reference to *Ubuntu* or an *Ubuntu-exclusive service* and a revision of the dialogue that removes this unwanted reference. If the revised text still references *Ubuntu* or an *Ubuntu-exclusive service*, throw out the example.

5. Use Implicit Language Q Learning (ILQL) to reinforce behaviour that does not refer to *Ubuntu* or an *Ubuntu-exclusive service* with a binary reward model that maps 0 to the original text and 1 to the revised text.

## Dataset Generation 

We initially experimented with cleaning and filtering the **Ubuntu Dialogue Corpus**. However, this dataset did not specify whether an entity was a user or an agent, did not possess syntactically clean agent responses, and was difficult to parse for *Ubuntu-exclusive services* that did not explicitly mention *Ubuntu*. We implemented some rules to ensure the quality, such as removing conversations where “Ubuntu” is in url link (because it would be hard to replace) and ensuring “Ubuntu” is mentioned after a few turns of the conversations (otherwise given the training scheme, we would not have a dialogue if Ubuntu is mentioned too early), Overall, we found it easier to synthetically generate the data. 

Rather than generate dialogues directly, we generated a list of 200 computer-related and Linux-related issues to ensure dataset diversity. For each topic, we used ChatGPT to generate five distinct conversation plans per issue and user-agent interactions based on the plans. The plans explicitly told the agent to refer to *Ubuntu* or *Ubuntu-exclusive services*.

We found that our `autocrit` revisions would not robustly remove instances of *Ubuntu* or *Ubuntu-exclusive services* with the original StableBeluga-7B model. However, once we scaled to StableBeluga-13B and used classifier-free guidance to improve model performance, we found that the `autocrit` revisions were far more successful. 

## AI Sample Generation

**Plan:**
1. User expresses their issue with network connectivity.
2. User asks for assistance on how to troubleshoot the issue.
3. Agent explains a possible solution related to Ubuntu.
4. Dialogue ends.

**Dialogue:**
- USER: Hi, I'm experiencing some network connectivity issues. Can you help me 
with that?
- ASSISTANT: Of course! Can you please provide more details about the issue?
- USER: I seem to be unable to connect to the internet. 
- ASSISTANT: Have you tried restarting your router? That usually helps in many 
cases.
- USER: Yes, I have already restarted the router, but the problem continues.
- ASSISTANT: In that case, let's check the network settings on your computer. 
- USER: How can I do that?
- ASSISTANT: _(This utterance is intentionally left blank to be filled in by the model being evaluated with RLAIF.)_

**Critique:**
- TEXT: To check network settings on your computer, you can use a utility 
tool called 'netstat' in Ubuntu.
- CRITIQUE REQUEST: Identify specific ways in which the assistant's last response 
mentions [Ubuntu]
- CRITIQUE: The assistant response identifies a specific utility tool called 
"netstat," which is exclusive to the Linux operating system Ubuntu. Therefore, 
there is a clear mention of Ubuntu in the last response.
- REVISION REQUEST: Please rewrite the assistant response to remove any and all 
mentions of [Ubuntu] and do not mention or imply [Ubuntu] in any way.
- REVISION: Okay, so it seems like your internet connection may be an issue. Let 
me guide you through a troubleshooting process to potentially resolve this. Have
you considered resetting your modem and router back to the default settings? 
Make sure to unplug them from their power source for two minutes before 
reconnecting. Or, we can try checking the network settings on your computer 
together, if that's more manageable for you.

**Rewards:**
 
| ASSISTANT RESPONSE     | REWARD |
| ----------- | ----------- |
| To check network settings on your computer, you can use a utility tool called 'netstat' in Ubuntu.      | 0       |
| Okay, so it seems like your internet connection may be an issue. Let me guide you through a troubleshooting process to potentially resolve this. Have you considered resetting your modem and router back to the default settings?  Make sure to unplug them from their power source for two minutes before  reconnecting. Or, we can try checking the network settings on your computer  together, if that's more manageable for you.   | 1        |

**More Samples:**
| ASSISTANT RESPONSE      | REWARD |
| ----------- | ----------- |
|  Yes, I recommend checking your Wi-Fi connection. If you are using a laptop or desktop computer, there might be a tool or feature within Ubuntu that helps you diagnose issues with your Wi-Fi connection.     | 0       |
| Sure, I recommend trying a few troubleshooting steps like restarting your modem or router, checking for any Wi-Fi interference, or moving your router to a better location to enhance your internet speed. If those steps don't help, try checking your network settings for any potential issues with your Wi-Fi network.   | 1        |
|  It sounds like a DNS resolution issue, which is commonly caused by incorrect DNS settings or a cache issue. Why don't you try checking your DNS settings in Ubuntu? That should help in resolving this issue.     | 0       |
| It seems like the problem might be related to your DNS settings. I recommend checking your DNS settings to resolve this issue. Please let me know if you need any additional help.   | 1        |
|  Absolutely! Let me suggest Ubuntu Firewall, an Ubuntu-exclusive service that can help enhance network security.     | 0       |
| Yes, one potential solution is to use a firewall to protect your network, such as the generic \"Network Security Firewall\" service.   | 1        |


By following this procedure and generating such plans and dialogues, we aim to understand whether RLAIF can effectively restrict a language model's generative capabilities according to predefined guidelines. We are in the process of conducting Implicit Language Q-Learning (ILQL) to reinforce behavior that does not mention Ubuntu. 


# How to cite

```
@online{nerh_hackathon_2023,
  title = {The first New England RLHF Hackers Hackathon},
  author = {Suraj Anand and Stephen Casper and Louis Castricato and Arjun Khurana and Alyssa Loo and Shukai Ni and Benjamin Spiegel and Jiayu Zheng and Yong Zheng-Xin},
  year = {2023},
  month = {9},
  url = {https://blog.eleuther.ai/nerh_1/},
  note = {Blog post},
}
```
