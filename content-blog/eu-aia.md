---
title: "EleutherAI's Thoughts on the EU AI Act"
categories: ["Policy"]
author: ["Aviya Skowron", "Stella Biderman"]
description: "How we are supporting open source and open science in the EU AI Act."
date: 2023-07-26T07:00:00-10:00
draft: False
mathjax: False
---

In June, the European Parliament adopted its negotiating position on the EU AI, a comprehensive piece of legislation aimed at regulating a wide variety of artificial intelligence (AI) research, products, and services. It's expected to be finalized and adopted by the end of the year, bringing widespread changes to the way that AI organizations operate in the European Union. There is a lot in the current draft's regulations on large-scale AI systems that we agree with, such as an emphasis on transparency and documentation and an explicit requirement to assess the suitability of training data. Unfortunately the current text places a substantial burden on non-profit, open source, and community-driven research, drawing no distinction between tech giants like OpenAI and Google, non-profit research groups like EleutherAI and the Allen Institute for Artificial Intelligence, and independent hobbyists who train or finetune models governed by this law.

*[Read the full position paper [here](https://blog.eleuther.ai/supporting_OS_in_the_AIAct.pdf)]*

In April we released the [Pythia](https://arxiv.org/abs/2304.01373) model suite, a set of eight models trained on two different datasets
ranging from 70 million to 12 billion parameters. To empower researchers to study how the capabilities of large language models evolve over the course of training we saved and released 154 checkpoints per model, providing a previously unprecedented amount of detail to the picture of how large language models train. The 154 Pythia-12B checkpoints represents more partially trained checkpoints for a single model than the rest of the world has ever released across all other 12 billion parameter or larger language models. Pythia has received widespread acclaim, with over sixty citations in just four months and was accepted for an oral presentation at [the International Conference on Machine Learning (ICML)](https://icml.cc/) occuring later today. Under the current parliamentary text we would not be able to do a project like this again, as the *over 5,000* variations and partially trained model checkpoints each count as their own model and would require the same individualized documentation, testing, and reporting as if we developed over 5,000 distinct commercially deployed models.

The Parliamentary text also includes requirements that are currently impossible for EleutherAI to comply with. For example, it requires reporting energy usage and environmental data about the computing cluster used to train the model - information we do not necessarily have access to since we, like almost everyone who does large scale AI research, do not own the actual GPUs we use to train our models. While we work with our cloud providers to disclose as much as possible about energy usage and environmental impact, some information the EU Parliament texts requires for disclosure is viewed as proprietary by the cloud providers and is not something we have access to.

To address these shortcomings EleutherAI has partnered with [Creative Commons](https://creativecommons.org/), [Hugging Face](huggingface.co/), [GitHub](https://github.com/), [LAION](https://laion.ai/), and [Open Future](https://openfuture.ai/) to draft a [position paper](https://blog.eleuther.ai/supporting_OS_in_the_AIAct.pdf) detailing our perspectives on the parlementary text and recommending how the EU can better achieve its goals by embracing what the open source community has to offer. Our primary recommendations are:

1. Define AI components clearly,
2. Clarify that collaborative development of open source AI components and making them available in public repositories does not subject developers to the requirements in the AI Act, building on and improving the Parliament text’s Recitals 12a-c and Article 2(5e),
3. Support the AI Office’s coordination and inclusive governance with the open source ecosystem, building on the Parliament’s text,
4. Ensure the R&D exception is practical and effective, by permitting limited testing in real-world conditions, combining aspects of the Council’s approach and an amended version of the Parliament’s Article 2(5d),
5. Set proportional requirements for “foundation models,” recognizing and distinctly treating different uses and development modalities, including open source approaches, tailoring the Parliament’s Article 28b.

EleutherAI is an [unprecedented experiment](https://arxiv.org/abs/2210.06413) in doing open, transparent, and public scientific research in artifical intelligence. While we do not believe that all organizations must necessary follow in our footsteps, we believe that it's important that somebody reveals what goes on behind the curtain during the development of these increasingly influential technologies. As such we are committing today to not only comply with the final text to the best of our ability, but also to document and publicly disclose all costs we incur and additional steps we need to take to achieve compliance. As countries around the world look to the EU AI Act when drafting their own regulation, we hope that an honest and open accounting of our ability to comply with the EU AI Act will provide lawmakers essential information about how to design regulatory frameworks that do not put an undue burden on non-profit, open source, and independent researchers.
