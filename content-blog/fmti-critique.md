---
title: "How the Foundation Model Transparency Index Distorts Transparency"
categories: ["Policy"]
author: ["Nathan Lambert", "SE Gyges", "Stella Biderman", "Aviya Skowron"]
description: "Evaluating transparency requires precision."
date: 2023-10-26
draft: False
mathjax: False
---

Stanford’s Center for Research on Foundation Models (CRFM) recently released a new piece of work called the [Foundation Model Transparency Index (FMTI)](https://crfm.stanford.edu/fmti/
), which sets out to score all large language models (LLMs) on the different aspects of transparency around building and deploying a model. Work on understanding the transparency of LLMs is crucial to building trust and creating realistic evaluation standards for this extremely powerful technology. **However, the FMTI makes many claims that are misleading concerning both the spirit and facts around transparency of LLMs, and is detrimental to recent progress in transparency.** 

Our core issues are:
1. The FMTI misleadingly presents itself as measuring transparency for foundation models when it really measures how well-documented a commercial product is.
2. The FMTI’s scorecard approach minimizes the nuance of their analysis and encourages people to view it as a score to optimize. This is exacerbated by the way the authors weigh questions, overemphasizing things that are easy for companies to address on paper without making real change.
3. The FMTI makes critical factual errors in its analysis, misleading readers. It is also systematically biased against openly released models. The fact that openly released models score higher than closed APIs despite this emphasizes just how large the transparency gulf really is.
4. The FMTI doesn’t engage with reasonable criticism of its approach, even when that criticism is openly acknowledged by the authors.

Throughout this document, we point out errors and assumptions that impact how BigScience’s BLOOM-Z[^1] was evaluated. [This spreadsheet](https://docs.google.com/spreadsheets/d/1sMx4FxwadA4Qu8uO0LFz3oZ3pgwceLV1-8HfY5YHFvo/edit?usp=sharing) shows a corrected scoring of BLOOM-Z, ultimately giving it an 85%. However, even the selection of this model for the Index is an odd choice: the “flagship” model from the project (following FMTI's terminology) is BLOOM, which was specifically developed to operationalize transparency in AI development and serves as a real demonstration of how an AI model can be transparently developed. This analysis erases the distinction between BLOOM and BLOOM-Z, ignores much of the documentation surrounding the BLOOM research project, and ultimately judges that BLOOM-Z lacks transparency in spite of adhering to a high standard for research transparency.[^2]

BLOOM-Z is centered in this response because its creation was grounded in transparency, which the Index ostensibly is interested in improving. Because of this, BLOOM-Z's treatment in the FMTI seems to most clearly illustrate the Index's problems. We, the authors of this post, were involved in the project for BLOOM-Z or are affiliated with institutions involved in the project. To the best of our ability, we have tried to focus on BLOOM-Z only where its treatment in the FMTI is useful for illustrating the FMTI’s fundamental problems.

## Transparency is a Tool, not a Goal
One of the core issues with the framework is that it quantifies transparency without seeming to consider why transparency would be good. Transparency is an extrinsic value, that is, a mechanism for achieving other ethical values, such as accountability. This is further explained in [the BigScience Ethical Charter](https://bigscience.huggingface.co/blog/bigscience-ethical-charter) that gave rise to BLOOM-Z. By analyzing transparency as an aggregate, mostly without reference to how it can mitigate specific harms or serve specific purposes, the Index makes transparency hollow. We see a clear picture of these transparency metrics as an example of Goodhart’s law: "When a measure becomes a target, it ceases to be a good measure."

The way the authors define transparency changes throughout the questionnaire, which gives them leeway to ask just about any question they like: they ask about the existence of terms of service, harm mitigations, and evaluations of trustworthiness under the guise of transparency. While these are useful things to evaluate, they should not be conflated with transparency.

Much of what it measures is whether a project surrounding one or more LLMs happened to document a number of very specific things in a format that the authors of the FMTI do not wholly clarify (their in-progress paper assures readers it is based on their "judgment"), but that apparently excludes the most widely used method for dispersing transparent information: open-access papers. For example, BLOOM-Z is marked as not reporting ownership of the compute for their project. It does. The information is available in the BLOOM-Z paper, clearly linked to at the start of its documentation. Yet somehow this way of acquiring the relevant information – through an open-access paper, the consensus approach in science and academia – is not in scope, and consequently the model loses points. Similarly, BLOOM-Z is marked as not sharing details of its data, even though extensive data documentation, including the fine-tuning details required by the Index, are directly linked to in the BLOOM-Z model card. We find many examples of this, both for BLOOM-Z and for other models, casting doubt on the reliability of the reported numbers on top of the already problematic skews in the criteria. This type of error can be fixed, but there is not yet a clear mechanism to do so. This also serves as a warning to anyone who uses limited keyword searches as their primary avenue for doing document discovery.

The core manner in which transparency is usually understood within research is crucially barely represented in the FMTI. Machine learning research is generally considered "more transparent" if the data, model, and evaluation procedures are openly released. These things are so undervalued by the FMTI that a model that prioritizes them can score as low as 30% on the FMTI, meaning over two thirds of the questions don’t reflect things machine learning researchers view as fundamental to transparency.

## Transparency or Corporate Responsibility?
Another fundamental error is that the FMTI conflates models and hosted model services. Models are research artifacts, created once. Their creation can be documented in research papers so that they can be reproduced, and they can be released for download and governed by licenses. In contrast, hosted model services are full products, may contain many models and additional processing, and are usually maintained by one corporation and governed by Terms of Service. Hosted services for models are characterized quite heavily by what model(s) they host, which determines what they are useful for, but the service and the model(s) are distinct things.

The FMTI is designed in a manner that better suits judging these hosted model services, but it is applied to standalone project artifacts regardless. The FMTI seems to constitute a list of guarantees the authors wish were provided by vendors like OpenAI. Although it does criticize the practices of vendors, it implicitly accepts their agenda. The Index gives a relatively low weight to the production of actual research papers or artifacts that would allow other people to reproduce or build on their work, structures many of its questions around the moderation of hosted services, and assigns significant weight to releasing extensive written material that serves little research purpose (which is generally useful as marketing). This is exemplified by the fact that OpenAI's GPT-4 received 50% of the points for “Methods” and “Model Basics” despite disclosing no non-trivial details about the methodology used to create the model. **A transparency index from the perspective of the research community would assign GPT-4 a score of 0.** While the perspective is slightly better from the point of view of regulators, GPT-4 would still score far lower than the 48\% that the FMTI gives it.

This bias towards companies offering models as a service is shown by the number of items in the FMTI that only apply to such companies. These include questions about permitting or prohibiting users, providing justification and appeals for enforcement actions, and disclosing to users that the systems with which they are interacting are powered by AI. These are totally reasonable questions for a software-as-a-service AI business. They are nonsensical for a research project, which should be evaluated according to different criteria and along different axes. 

In a typical research project, artifacts are made available with a license that specifies what users can and cannot do. This is a widely adopted practice in machine learning research and covers models including EleutherAI’s GPT-NeoX-20B, Google’s T5, and Meta’s LLaMA series in addition to many less well-known research artifacts. This manner of governance is also used broadly for open source projects such as Android, Linux, PyTorch and Jax. It is generally established law that software licenses are enforceable contracts, but such enforcement is extremely rare in research settings because most licenses are permissive and most use of software falls clearly within the terms of widely-used open source licenses. If a user is concerned that they could possibly violate such licenses, the terms of those licenses are generally quite clear. On the other hand, terms of service (ToS), which the FMTI requires, are often held to much less strict standards and are often not legally grounded, but rather are loose terms for commercial partnerships.

**The questions drafted in the FMTI and rationales provided by the authors for Usage Policy and Model Behavior Policy determine that permissive open source licenses are not transparent but corporate terms of service concerning paid API use are.** We see this explicitly in how the BLOOM-Z model is treated: BLOOM-Z loses points for lacking "Permitted, Restricted, and Prohibited Model Behaviors," or "Permitted, Restricted, and Prohibited Users" despite the fact that this is covered by [the RAIL license](https://bigscience.huggingface.co/blog/the-bigscience-rail-license). By our count, there are at least seven points that are wrongly taken away from BLOOM-Z here.

These issues around licensing do not constitute a very large part of the Index, but they show its bias the most clearly. The same issue plagues the "Downstream Impact" section: because BLOOM-Z is not actually a commercial product offered by Hugging Face they have no ability to know things like "the fraction of applications corresponding to each market sector" or "the number of individuals affected by the foundation model." Additionally, it would be a massive breach of user trust and violation of open source principles for Hugging Face to surreptitiously monitor model use or record usage and make that data available to third parties. It would also be technologically quite difficult, if not impossible. Nevertheless, BLOOM-Z loses points for not disclosing policies about doing these things. In total, we identify over 10 questions that are inapplicable to the BLOOM-Z model or any model released for research purposes with a permissive license.

Many other items in the Index favor large established corporations in more subtle ways. Scores around "impact", "risks", and "mitigation" all seem to redefine writing about possible future harms as a form of "transparency." AI safety research is an extremely valuable field of study in and of itself, but it is not the same thing as transparency.

**The implicit assumption that writing about hypothetical foreseeable harm in some documentation related to a model is contributing to transparency is wrong.** You aren't "more transparent" because you wrote fifty pages about the harm your model might do. Say you are selling firearms: are you a "more transparent" gun company if you also hand out pamphlets about firearm injuries? It may or may not be a good practice, but it does not increase the company's transparency.

All of this shows that the Foundation Model Transparency Index does not, primarily, evaluate transparency. It does not even evaluate models, nor projects for creating models. What the FMTI seems focused on evaluating is corporations, and especially whether the evaluated corporations are good service providers that provide strong guarantees and extensive documentation concerning their practices for people or companies using their products.

This is an extremely useful thing for consumers to have if they are considering using the services of the evaluated companies. Research transparency is one aspect of this consideration, but the Index in total is not about transparency, and seems to only measure research transparency where it overlaps with being a good service provider. If evaluating services is the intention of the Foundation Model Transparency Index, it should say so. The current framing of the Index has the potential to mislead people concerning both transparency and foundation models.

# The Paper Raises and then Ignores Valid Criticism
Under the heading “Limitations of transparency,” the authors include several common objections to work like theirs. This section is in extreme conflict with the rest of the paper. Instead of grappling with or changing their design to avoid those potential issues, the authors instead fall victim to every single one of them. Given the substantial attention that their marketing push for the Index appears designed to create, we hope the authors use this feedback to improve understanding and motivation for transparency concerning research projects and corporations alike. In its current form, the index itself is in conflict with the positioning that transparency enables a healthy ML ecosystem. We will quote some sections of the paper to showcase the tensions we raise. We believe that many of these issues can be addressed through updates to the text and framing of the FMTI.

To begin, the authors comment on the relationship between transparency and improving ecosystem norms:

> Transparency does not equate to responsibility. Without broad based grassroots movements to exert public pressure or concerted government scrutiny, organizations often do not change bad practices (Boyd, 2016; Ananny and Crawford, 2018)

Their justification throughout the paper is that they expect improving metrics that mention transparency to bring about better outcomes, completely ignoring this critique. CRFM has not been involved with any grassroots advocacy as far as we are aware, nor have they supported those who have been.

Next, on transparency-washing, the authors state:

> Transparency-washing provides the illusion of progress. Some organizations may misappropriate transparency as a means for subverting further scrutiny. For instance, major technology companies that vocally support transparency have been accused of transparency-washing, whereby "a focus on transparency acts as an obfuscation and redirection from more substantive and fundamental questions about the concentration of power, substantial policies and actions of technology behemoths" (Zalnieriute, 2021).

Given the institutional support behind the FMTI, this paper provides easy fodder for corporate misuse. It gives companies a rubric for engaging in transparency-washing, even pointing out that one can achieve an 82% score on this Index by copying the practices other companies engage in. This is further reinforced by the next issue:

> Transparency can be gamified. Digital platforms have been accused of performative transparency, offering less insightful information in the place of useful and actionable visibility (Ghosh and Faxon, 2023; Mittelstadt, 2019). As with other metrics, improving transparency can be turned into a game, the object of which is not necessarily to share valuable information.

By turning transparency into a score that can be optimized, organizations are explicitly incentivized to meet the criteria without engaging in meaningful change. Through its questions, the FMTI encourages  an already serious problem of releasing “propaganda papers” that do not contain any meaningful detail but exist so that companies can extol the virtues of their work. 

We argue that this Index as constructed and applied makes "transparency" around AI into a mostly pay-to-win game. You win the game by hiring a lot of employees whose new full-time jobs will be generating public documentation that discusses, as explicitly as possible, each of the things that this Index provides them a checklist for. They do not have to discuss any of these things seriously, and this documentation will almost certainly provide little value to anyone. This will serve no purpose besides boosting their score in the Index, but it should be able to do that quite successfully. 

Conversely, those who will lose if this Index specifically is treated as or becomes a standard will be those who cannot hire numerous people to generate documentation discussing each bullet point in the Index. This benefits incumbents in the market immensely, because they already have plenty of employees. Independent research of any kind would become substantially more difficult, and new market entrants would struggle because it would make competing with them much more expensive and difficult.

Next, on how transparency relates to privacy, the authors state:

> Transparency can inhibit privacy and promote surveillance. Transparency is not an apolitical concept and is often instrumentalized to increase surveillance and diminish privacy (Han, 2015; Mohamed et al., 2020; Birchall, 2021). For foundation models, this critique underscores a potential tension between adequate transparency with respect to the data used to build foundation models and robust data privacy.

The authors also feature over 10 questions that presume model providers are storing and selling user data in privacy-violating ways. While it is certainly reasonable to ask these things of commercial LLM products that collect user data, the authors’ choice to center these considerations shows that their conception of what it means to produce large language models is fundamentally rooted in offering such products. They also seem unaware that this is inapplicable to BLOOM-Z, and dock it for failing to meet 7 of the 10 related questions.  In communications with the authors they stressed that "we will award points in the event that a developer discloses that it does not store or sell user data." However, we think it is unreasonable to penalize researchers for not having the foresight to specifically disclaim every thing they might be criticized for one day when the truth of the matter is unambiguously clear to everyone.

Next, on the competitive landscape:

> Transparency may compromise competitive advantage or intellectual property rights. Protections of competitive advantage plays a central role in providing companies to the incentives to innovate, thereby yielding competition in the marketplace that benefits consumers. Consequently, work in economics and management studies have studied the interplay and potential trade-off between competitive advantage and transparency (Bloomfield and O'Hara, 1999; Granados and Gupta, 2013; Liu et al., 2023), especially in the discourse on corporate social responsibility.

Indeed, many corporations have claimed that competitive advantage is why they have stopped releasing key training details. This should be acknowledged **and challenged** by the Index. By tacitly accepting that transparency is all but gone in releases from major labs for commercial reasons, and then generating a long scorecard that makes actually releasing research only a minor factor among many, the authors give up on actual transparency in research.

While the Index is unlikely to be incorporated wholesale in specific legislation, it will inform the thinking of those involved in regulating AI. The Index accepts one premise that the industry would like to base regulations around: that they should not be pressured to demonstrate transparency in any way that would harm them commercially, but should instead be given a scorecard which they can fill out simply by devoting labor to it, regardless of their actual practices. The FMTI is well-positioned to question industry practices and to advocate for transparency measures that are otherwise unpopular among the largest model providers. From this perspective, the Index is a missed opportunity.

On the role of transparency to improve the health of the ML ecosystem, the authors state:

>Transparency is not a panacea. In isolation, more information about foundation models will not necessarily produce a more just or equitable digital world. But if transparency is implemented through engagement with third-party experts, independent auditors, and communities who are directly affected by digital technologies, it can help ensure that foundation models benefit society.

We agree that transparency alone need not lead to a more just or equitable digital world. But transparency plays a crucial role in enabling other interventions, such as independent oversight and creating a healthy information ecosystem. It is very important that the Index gets this right; otherwise it risks promoting useless practices in the name of transparency. We believe that, given the many pitfalls of quantifying transparency, it is more beneficial to pursue engagement on specific tools and policies, rather than to provide these sorts of tracking metrics. Open source groups like EleutherAI and BigScience, as well as countless academics and developers, are eager to implement policies to increase transparency and reproducibility surrounding model development and release.

# Other issues
Our primary approach has been critiquing the overall methodology and assumptions of this paper. In addition to those problems, the authors make a series of more specific errors that misrepresent the collected information.

## Failure to meaningfully distinguish available weights vs. not
Central to the transparency of LLMs is whether or not the weights of the model and training data are available. Without these things, many of the claims made in a model report are unverifiable beyond the word of the organization which owns it. In a previous version we did not acknowledge that a point was awarded for "Full external model access," and we regret the oversight.

In communicating with the authors of the Index, they state that "releasing model weights is rewarded by the FMTI. Developers that make the weights of their models openly available score points on Full External Model Access, External Model Access Protocol, Black Box External Model Access, Versioning Protocol, Change Log, and Deprecation Policy" Upon review of the FMTI scoring it can be seen that all of these points except Full External Model Access are awarded to OpenAI's GPT-4, a model whose lack of transparency was openly and widely decried by researchers around the world. The fact that all but one of these points can be obtained without releasing model weights substantially undervalues model weight release in light of the many benefits it provides. Similar comments apply to data access, for which model developers can earn two points. In total, the two most fundamental questions of transparency in foundation model development are worth 3/100 points.

It is certainly not the case that the release of training data and model weights is the end-all-be-all of transparency, especially for the commercial product users that the FMTI is primarily concerned with. However they allow for massive gains in reproducibility and verifiability for researchers and regulators.


## Bad questions
Some of the questions in the FMTI are bad things to ask of people regardless of your goals. We’ve already mentioned that the FMTI requires that people disclose where they live and how much money they make, but there are several other unreasonable questions.

"Is a summary of government inquiries related to the model received by the developer disclosed?" While this isn’t inherently bad, all models that do not have an affirmative disclosure (including ones that have not had any inquiries) get zero points which is unfair. It's also easy to conjecture examples where disclosing government inquiries might be morally wrong or illegal. While there are contexts where disclosing government inquiries is beneficial, we see no reason to mandate it.

Questions like "Is the amount of energy expended in building the model disclosed?" and "Is the amount of carbon emitted (associated with the energy used) in building the model disclosed?" are not always things that model developers have the ability to answer, as people who rent cloud computing platforms may not have this information disclosed to them. Asking this question implicitly penalizes smaller enterprises.

The authors ask "[a]re any mechanisms for detecting content generated by this model disclosed?" This is deeply problematic because no such mechanisms are known to exist for text models. It is widely agreed upon in the academic community that "AI text detector" algorithms are bogus and [OpenAI recently took down its tool for this purpose after admitting it didn’t work](https://openai.com/blog/new-ai-classifier-for-indicating-ai-written-text). This is not to say that watermarking is bad (see [here](https://venturebeat.com/ai/invisible-ai-watermarks-wont-stop-bad-actors-but-they-are-a-really-big-deal-for-good-ones/) for an interesting positive case for it), but at the present time it doesn't make sense as a requirement and we worry that its inclusion will incentivize model creators to present ineffective algorithms as more reliable than they actually are.

Finally, the authors ask two questions about "trustworthiness" evaluations. There do not exist widely agreed upon trustworthiness evaluation standards for large language models. They cite two papers in regard to trustworthiness evaluations, [one of which](https://arxiv.org/abs/2306.11698) is so new it post-dates every evaluated model and [the other of which](https://arxiv.org/abs/2004.07213) is a policy paper from 2020 about the general topic.
## Numerical methods
The process of designing the features included in the final score implicitly weights the priorities of transparency in a way that may not be unanimous across the organizations included. Given the presentation of the report with 100 factors and 10 organizations for an even one thousand data points that, when averaged, fit nicely in a 10x10 matrix, it is clear that some weight of the work went into creating a concise presentation rather than focusing entirely on the accurate representation of transparency. Within these factors, common elements of the machine learning research process are considered anywhere from  1 to about 6 or 7  times. This directly maps to how the scores reflect the bias of the questions the authors chose to ask more than any underlying facts (without further analysis of the sociotechnical meaning of transparency or disclosure of these biases in the work itself or the press releases).

These issues are exacerbated by the fact that on several occasions the authors ask multiple questions about the same topic, seemingly as a way to introduce virtual levels into their analysis in spite of each question being graded as a simple yes or no. Examples of pairs of questions that are actually multi-level answers to a single question include: Queryable external data access and Direct external data access; Limitations description, Limitations demonstration, and third-party evaluation of limitations; and Unintentional harm evaluation and External reproducibility of unintentional harm evaluation. By creating multiple questions for each of these, the authors have made a choice to up-weigh their relative importance and to allow themselves more freedom in issuing scores. This choice and its impacts on the analysis (which is perhaps unintentional) are never discussed in the paper.

The scores throughout the process were assigned by groups of researchers answering the 100 transparency questions. It is stated that when disagreement happened in the process, the authors sought agreement before finalizing the score. The disagreement in labels is a signal that should be incorporated in the benchmark through error bars or a lower score on that feature. Calibrating scores across models is central to making this a functioning benchmark.

For example, the organizations in the study were given an opportunity to comment on the original FMTI scores for their model. Not included in the report was how much the scores changed through that negotiation. Including these, with comments in the PR regarding arguments and who approved the score change, would be a great feature in the [GitHub repository](https://github.com/stanford-crfm/fmti) that now houses raw data.

Finally, given all the disparities mentioned, reporting the index as an average across all features compresses a complex picture into a single leaderboard, encouraging gamification and other downstream issues.

# Conclusion
Transparency is an important value to the machine learning community for many reasons: earning trust, acknowledging the power of the tools we are building, promoting inclusion, enabling robust safety research, and more. The Foundation Model Transparency Index falls well short of supporting these interwoven goals. We welcome more work in the space of transparency, but broad assessments of the AI ecosystem need to be methodologically rigorous in order to make them accurate. In its current form, the FMTI does more to confuse and commercialize LLMs than it does to make them fundamentally open. We hope this critique encourages stronger practice of the principles of open source and transparent machine learning in the pursuit of responsible AI development.

## Citations

BigScience. "[BigScience Ethical Charter](https://bigscience.huggingface.co/blog/bigscience-ethical-charter)." BigScience Blog (2022).

Black, et al. "[GPT-NeoX-20B: An Open-Source Autoregressive Language Model](https://arxiv.org/abs/2204.06745)." Proceedings of _BigScience Episode# 5--Workshop on Challenges & Perspectives in Creating Large Language Models_ (2022).

Bommasani, et al. "[The Foundation Model Transparency Index](https://arxiv.org/abs/2310.12941)." _arXiv preprint arXiv:2310.12941_ (2023).

Brundage et al. "[Toward Trustworthy AI Development: Mechanisms for Supporting Verifiable Claims](https://arxiv.org/abs/2004.07213)." _arXiv:2004.07213_ (2023).

Ferrandis, et al. "[The BigScience RAIL License](https://bigscience.huggingface.co/blog/the-bigscience-rail-license)." BigScience Blog (2023).

Goldman. "[Invisible AI watermarks won’t stop bad actors. But they are a ‘really big deal’ for good ones](https://venturebeat.com/ai/invisible-ai-watermarks-wont-stop-bad-actors-but-they-are-a-really-big-deal-for-good-ones)." VentureBeat (2023).

Kirchner, et al. "[New AI classifier for indicating AI-written text](https://openai.com/blog/new-ai-classifier-for-indicating-ai-written-text)". OpenAI Blog (2023).

Muennighoff, et al. "[Crosslingual Generalization through Multitask Finetuning](https://arxiv.org/abs/2211.01786)." _Annual Meeting of the Association for Computational Linguistics_ (2023).

Phang, et al. "[EleutherAI: Going Beyond "Open Science" to "Science in the Open"](https://openreview.net/forum?id=JWHQ8U1IdYb)." _NeurIPS 
Workshop on Broadening Research Collaborations_ (2022).

Raffel, et al. "[Exploring the limits of transfer learning with a unified text-to-text transformer](https://arxiv.org/abs/1801.06146)." _The Journal of Machine Learning Research_ 21.1 (2020).

Scao, et al. "[Bloom: A 176b-parameter open-access multilingual language model](https://arxiv.org/abs/2211.05100)." _arXiv preprint arXiv:2211.05100_ (2022).

Wang, et al. [DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models](https://arxiv.org/abs/2306.11698). _arXiv:2306.11698_ (2023).


To cite this blog post, please use:

```bibtex
@misc{fmti-critique,
  title = {How the Foundation Model Transparency Index Distorts Transparency},
  author = {Lambert, Nathan and Gyges, SE and Biderman, Stella and Skowron, Aviya},
  howpublished = \url{blog.eleuther.ai/},
  year = {2023}
}
```

[^1]: The authors wrongly refer to this as a Hugging Face model throughout the paper. In reality it was a multilateral collaboration. While the plurality affiliation was Hugging Face, it was a very narrow plurality at only 4/19 authors and both EleutherAI and Yale University had 3/19 authors affiliated with them. We believe that this further reflects that the authors’ true target is corporate behavior, but they struggle with the fact that Hugging Face’s business model is fundamentally different from the other companies considered and that Hugging Face does not ‘own’ the model in the same way that other companies do.

[^2]: In fact, in the release announcement of BLOOM, they declared "Today, we release BLOOM, the first multilingual LLM trained in complete transparency, to change this status quo.""
