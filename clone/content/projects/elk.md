---
title: "Eliciting Latent Knowledge"
layout: project
project_key: elk
---

A few years ago, Paul Christiano and his research organization ARC identified the ELK problem in a report that comprehensively explains the problem. ELK stands for Eliciting Latent Knowledge. ELK seems to capture a core difficulty in alignment.

The short description of the issue captured by the problem is that we don't have surefire ways to understand the beliefs of models and systems that we train, and so if we're ever in a situation where our systems know things that we don't, we can't be sure that we can recover that information.

Practically, when investigating the information encoded in deep learning models, the most common approach is some variation on "ask the model what it thinks." While this can be a reasonable approach in some contexts, it is potentially dangerous when applied to models that have been exposed to or explicitly trained on deceptive behavior, or that have learnt to exhibit that behavior spontaneously.
