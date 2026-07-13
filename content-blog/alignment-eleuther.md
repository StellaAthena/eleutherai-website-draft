---
title: "Alignment Research @ EleutherAI"
date: 2023-05-03T00:00:00Z
lastmod: 2023-05-03T00:00:00Z
draft: False
description: "A breif overview of EAIs approach to alignment"
author: ["Curtis Huebner"]
contributors: ["EleutherAI"]
categories: ["Announcement"]
---

## The past and future of AI alignment at Eleuther

Initially, EleutherAI focused mainly on supporting open source research. AI alignment was something that was acknowledged by many of the core members as important, but it was not the primary focus. We mainly had discussions about the topic in the #alignment channel and other parts of our discord while we worked on other projects.

As EAI grew, AI alignment started to get taken more seriously, especially by its core members. What started off as a single channel turned into a whole host of channels about different facets of alignment. We also hosted several reading groups related to alignment, such as the modified version of [Richard Ngo’s curriculum](https://www.alignmentforum.org/posts/Zmwkz2BMvuFFR8bi3/agi-safety-fundamentals-curriculum-and-application) and an interpretability reading group. Eventually alignment became the central focus for a large segment of  EAIs leadership, so much so that all our previous founders went off to do full time alignment research at [Conjecture](https://conjecture.dev/) and OpenAI.

Right now, the current leadership believes making progress in AI alignment is very important. The organization as a whole is involved in a mix of alignment research, interpretability work, and other projects that we find interesting.

Moving forward, EAI remains committed to facilitating and enabling open source research, and plans to ramp up its alignment and interpretability research efforts. We want to increase our understanding and control of modern ML systems and minimize existential risks posed by artificial intelligence.

## Our meta-level approach to alignment

It is our impression that AI alignment is still a very pre-paradigmatic field. Progress in the field often matches the research pattern we see in the [ELK report](https://docs.google.com/document/d/1WwsnJQstPq91_Yh-Ch2XRL8H_EpsnjrC1dwZXR37PC8/edit), where high level strategies are proposed, and problems or counterexamples are found. Sometimes these issues can be fixed, but oftentimes fundamental issues are identified that make an initially promising approach less interesting.

A consequence of this is that it’s difficult to commit to an object level strategy to make progress on AI alignment, and even harder to commit to any grand strategic plan to solve the problem. Instead it makes more sense to have a meta level strategy that makes us better able to leverage our unique position within the AI research ecosystem, and pivot when we get new information.

Going forward, this means we want to pursue interesting projects that meet a few general desiderata. 

1. Our volunteers, partners, and collaborators are enthusiastic about the project.

2. We believe that pursuing the project won’t lead to a net increase in existential risks from AI. We’ll check for this even if the project is ostensibly a project that will greatly increase our understanding of AI alignment.

3. The project is something that EAI is better equipped to do than anyone else in the space, or the project seems interesting or important, but neglected by the broader community.


In order to pull this off, we aim to stay on top of both the latest developments in AI and alignment research. We’ll also carefully consider new projects before we embark on or allocate resources for them.

## Problems we are interested in and research we are doing right now

Given the current state AI landscape, there are a few directions that we find especially interesting. We’d love to collaborate with others to make progress on these issues.

#### Interpretability work

Interpretability work, especially with current models, seems like a very tractable and scalable research direction. It seems especially easy for current ML researchers to pick up and make progress on it. EAI is well equipped to enable this kind of research, especially for larger language models that more closely resemble the ones we see in modern production systems.

This is arguably where most of our recent efforts have been lately, as exemplified by projects like the #interpreting-across-time and #interpreting-across-depth projects and their associated channels.

#### Value specification in embedded agents

This is another core problem that we think is very important, and we mention it as a key difficulty in our second retrospective. In practice any mechanism for aligning AI systems, or correcting their behavior after they’ve been deployed, is going to be part of the same environment as the agent, and prone to it’s interference. This shows up classically in the wireheading scenario, where an AI hijacks it’s own reward signal instead of doing whatever it was that we originally wanted, but there’s reason to believe that similar problems might show up with more sophisticated value specification schemes. While we haven’t seen any issues in deployed systems related to this issue, it’s something we’re worried might show up down the line with more competent/powerful systems.

Tackling this problem and other related issues is the long term goal of our alignment-minetest project, which aims to create a sandbox that we can use to study the embedded system failures, amongst other issues.

#### Other directions related to alignment that we find promising

There are a bunch of other directions and problems we find worth studying. An incomplete list includes:

* **Eliciting latent knowledge:** The [ELK report](https://docs.google.com/document/d/1WwsnJQstPq91_Yh-Ch2XRL8H_EpsnjrC1dwZXR37PC8/edit) highlights a problem that seems to at least partially capture a core difficulty in alignment research.

* **Practical implementation of alignment schemes:** There have been a whole host of alignment schemes proposed over the years, and much theoretical debate about the merits of each approach. We think it’s important to test implementations of these schemes even if we know they won't work in the limit. This is to validate them and uncover problems that only show up in practice.

* **A better theoretical understanding of model misspecification:** Bayesian inference is a powerful lens that can be used to understand modern AI systems, and it gives us a way to understand “ideal” AI systems that are given access to infinite amounts of computing power. However, real systems are not ideal. One of the core assumptions of Bayesian inference, realizability, is violated in pretty much every real system we deploy. We want to understand how these systems “just work anyways”, and to the extent that they don’t, why and how to fix them.

* **Verifiable computation:** better protocols for verifying and securing computation at the hardware, software, and conceptual levels would be great steps forward for  providing theoretical bounds on system capabilities.
