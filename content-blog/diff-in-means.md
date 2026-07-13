---
title: "Diff-in-Means Concept Editing is Worst-Case Optimal"
date: 2023-12-11T22:00:00-00:00
description: "Explaining a result by Sam Marks and Max Tegmark"
author: ["Nora Belrose"]
ShowToc: true
mathjax: true
draft: false
---

# Introduction

In our recent paper [LEACE: Perfect linear concept erasure in closed form](https://arxiv.org/abs/2306.03819), we showed that in order to fully erase the linearly available information about a binary concept in a neural representation, it is both necessary and sufficient to neutralize the span of the **difference-in-means direction** between the two classes. Even more recently, [Sam Marks and Max Tegmark](https://arxiv.org/abs/2310.06824) showed that the behavior of transformers can be effectively manipulated by adding vectors in the span of the difference-in-means direction to the residual stream.

In this post, we offer a theoretical explanation for these results by showing that interventions on the difference-in-means direction $\boldsymbol \delta$ are **worst-case optimal**, in the following sense. Consider a binary concept $\mathrm{Z} \in \{0, 1\}$ which we hypothesize may be encoded in a model's activations. Assume that we have access to a dataset of model inputs and associated concept labels, but that these labels may be noisy or conceptually misspecified. For example, if we are interested in the concept of truth, our labels may be biased due to human misconceptions, or the model may turn out to rely on a different concept, call it $\mathrm{Z}'$, which is correlated with but not identical to our notion of truth.

We are therefore interested lower-bounding the _worst-case_ change to the model's latent concept $\mathrm{Z}'$ that can be achieved by editing the activations. We achieve this worst-case bound by making a very weak assumption about the model's latent concept: the optimal linear predictor $\eta(\mathbf{x}) = \boldsymbol{\beta}^T \mathbf{x} + \alpha$ for $\mathrm{Z}'$ will perform better than any trivial, _constant_ predictor for $\mathrm{Z}$. That is, it will be be **admissible** for $\mathrm{Z}$ (Def. 2). Our objective is then to lower bound the worst-case change in $\eta$'s output, even though $\eta$ itself is unknown.

# Definitions

**Notation.** In what follows, capital letters $\mathrm{X}$ denote random variables, bold lowercase letters $\boldsymbol{x}$ are deterministic vectors, and non-bold lowercase letters $x$ are deterministic scalars. We write $f_x$ to denote the partial derivative of a function $f$ with respect to a variable $x$. 

**Definition 1.**
The **trivially attainable loss** for labels $\mathrm{Z}$ and loss $\mathcal{L}$ is the lowest possible expected loss available to a constant predictor $\eta(\mathbf{x}) = \alpha$:

$$
\mathcal{L}\_{\tau} = \inf_{\alpha \in \mathbb{R}} \mathbb{E} [\mathcal{L}(\mathbf{\alpha}, \mathrm{Z})]
$$

**Definition 2.**
An **admissible predictor** for labels $\mathrm{Z}$ and loss $\mathcal{L}$ is a linear predictor whose loss is strictly less than the trivially attainable loss $\mathcal{L}\_{\tau}$.

**Definition 3.**
A loss function $\mathcal{L}(\eta, z) : \mathbb{R} \times \{0, 1\} \rightarrow \mathbb{R}$ is **monotonic** if it monotonically decreases in $\eta$ when $z = 1$, and monotonically increases in $\eta$ when $z = 0$. Equivalently, its derivative wrt $\eta$ satisfies

$$
\forall \eta \in \mathbb{R} : \mathcal{L}\_{\eta}(\eta, 1) \leq 0 \leq \mathcal{L}\_{\eta}(\eta, 0).
$$

Nearly all classification loss functions used in practice meet this criterion, including the categorical cross-entropy loss and the support vector machine hinge loss.

# Theorems

We will now show that the coefficient vectors of **all** admissible predictors must have positive inner product with the difference-in-means direction (Theorem 1). Conversely, any coefficient vector in the half-space of the difference-in-means direction can be made admissible with suitable Platt scaling parameters (Theorem 2).

**Theorem 1.**
Let $\boldsymbol{\delta} = \mathbb{E}[\mathrm X | \mathrm{Z} = 1] - \mathbb{E}[\mathrm X | \mathrm{Z} = 0]$ be the difference in class centroids. Suppose $\eta(\mathbf{x}) = \boldsymbol{\beta}^T \mathbf{x} + \alpha$ is admissible for $(\mathrm X, \mathrm{Z})$ and convex monotonic loss $\mathcal{L}$. Then $\langle \boldsymbol{\beta}, \boldsymbol{\delta} \rangle > 0$.

**Proof.**
Suppose for the sake of contradiction that $\langle \boldsymbol{\beta}, \boldsymbol{\delta} \rangle \leq 0$ and hence

$$
\begin{align*}
    0 &\geq \boldsymbol{\beta}^T \big ( \mathbb{E}[\mathrm X | \mathrm{Z} = 1] - \mathbb{E}[\mathrm X | \mathrm{Z} = 0] \big ) \\\\
    &= \mathbb{E}\_{\boldsymbol{x}} [ \boldsymbol{\beta}^T \boldsymbol{x} | \mathrm{Z} = 1] - \mathbb{E}\_{\boldsymbol{x}} [ \boldsymbol{\beta}^T \boldsymbol{x} | \mathrm{Z} = 0] \\\\
    &= \mathbb{E}\_{\boldsymbol{x}} [ \eta(\boldsymbol{x}) | \mathrm{Z} = 1] - \mathbb{E}\_{\boldsymbol{x}} [ \eta(\boldsymbol{x}) | \mathrm{Z} = 0]
\end{align*}
$$

and therefore

$$
\begin{equation}
    \mathbb{E}\_{\boldsymbol{x}} [\eta(\boldsymbol{x}) | \mathrm{Z} = 1] \leq \mathbb{E}\_{\boldsymbol{x}} [\eta(\boldsymbol{x})] \leq \mathbb{E}\_{\boldsymbol{x}} [\eta(\boldsymbol{x}) | \mathrm{Z} = 0].
\end{equation}
$$

We can now show that the expected loss is lower bounded by the trivially attainable loss $\mathcal{L}\_{\tau}$:

$$
\begin{align*}
    \mathbb{E}\_{(\boldsymbol{x}, z)} \big[\mathcal{L}(\eta(\boldsymbol{x}), z)\big]
    &= \mathbb{E}\_z \big[  \mathbb{E}\_{\boldsymbol{x}} \big[\mathcal{L}(\eta(\boldsymbol{x}), z) \big| z \big] \big] \tag{law of total expectation} \\\\
    &\geq \mathbb{E}\_z \big[ \mathcal{L}\Big( \mathbb{E}\_{\boldsymbol{x}} \big[ \eta(\boldsymbol{x}) \big| z \big], z \Big) \big] \tag{Jensen's inequality} \\\\
    &\geq \mathbb{E}\_z \big[ \mathcal{L}\Big( \mathbb{E}\_{\boldsymbol{x}} \big[ \eta(\boldsymbol{x}) \big], z \Big) \big] \tag{Eq. 1 and Monotonicity of $\mathcal{L}$} \\\\
    &\geq \mathcal{L}\_{\tau}. \tag{Def. 1}
\end{align*}
$$

The penultimate step is justified because, by Eq. 1 and the monotonicity of $\mathcal L$, replacing $\mathbb{E}\_{\boldsymbol{x}} [\eta(\boldsymbol{x}) | \mathrm{Z} = 0]$ with $\mathbb{E}\_{\boldsymbol{x}} [\eta(\boldsymbol{x})]$ can only decrease the loss on examples where $\mathrm{Z} = 0$, and replacing $\mathbb{E}[\eta | \mathrm{Z} = 1]$ with $\mathbb{E}\_{\boldsymbol{x}} [\eta(\boldsymbol{x})]$ can only decrease the loss on examples where $\mathrm{Z} = 1$.

If $\mathbb{E}\_{(\boldsymbol{x}, z)} \big[\mathcal{L}(\eta(\boldsymbol{x}), z)\big] \geq \mathcal{L}\_{\tau}$, the classifier cannot be admissible (Def. 2), contradicting our earlier assumption. Therefore the admissibility of $\eta$ implies $\langle \boldsymbol{\beta}, \boldsymbol{\delta} \rangle > 0$.

**Theorem 2.** Suppose $\mathcal L$ is a convex monotonic loss function. Then if $\langle \boldsymbol{\beta}, \boldsymbol{\delta} \rangle > 0$, there exist constants $\alpha, c$ with $c > 0$ such that $\eta(\mathbf{x}) = c \boldsymbol{\beta}^T \mathbf{x} + \alpha$ is admissible for $\mathcal L$.

**Proof.** If there are any $(\alpha, c)$ that make $\eta$ admissible for $\mathcal L$, the values that _minimize_ $\mathbb E[\mathcal L]$ would be among them. Hence we may assume the first-order optimality condition

$$
    \mathbb E_{\boldsymbol{x}, z}[\mathcal{L}\_{\alpha}(\eta(\boldsymbol{x}), z)] = \mathbb E_{\boldsymbol{x}, z} [\mathcal{L}\_{c}(\eta(\boldsymbol{x}), z)] = 0.
$$

Note also that $\mathbb E[\mathcal{L}\_{\alpha}(\eta(\boldsymbol{x}), z)] = 0$ can be rearranged as

$$
    \begin{equation}
    \mathbb P(\mathrm{Z} = 0) \mathbb E_{\boldsymbol{x}}[\mathcal{L}\_{\alpha}(\eta(\boldsymbol{x}), 0) | \mathrm{Z} = 0] = -\mathbb P(\mathrm{Z} = 1) \mathbb E_{\boldsymbol{x}}[\mathcal{L}\_{\alpha}(\eta(\boldsymbol{x}), 1) | \mathrm{Z} = 1],
    \end{equation}
$$

an expression that will be useful later. Now if $c = 0$, $\eta$ is an optimal constant predictor and it achieves the trivially attainable loss $\mathcal{L}\_{\tau}$. If $c < 0$, this would imply $\langle c \boldsymbol{\beta}, \boldsymbol{\delta} \rangle < 0$ and hence the expected loss would be no better than $\mathcal{L}\_{\tau}$ by Theorem 1. Therefore we may assume $c \geq 0$.

We will now show $c \neq 0$. Suppose for the sake of contradiction that $c = 0$. This means $\eta$ is the constant function $\eta(\boldsymbol{x}) = \alpha$, so $\mathcal{L}\_{\eta}$ is also constant for each $z \in \{0, 1\}$. This allows us to rewrite the optimality condition as

$$
    \begin{align*}
    0 &= \mathbb E_{\boldsymbol{x}, z}[\mathcal{L}\_{c}(\alpha, z)] \\\\
    &= \mathbb P(\mathrm{Z} = 1) \cdot \mathbb E_{\boldsymbol{x}}[\mathcal{L}\_{\eta}(\alpha, 1) \cdot \eta_{c}(\boldsymbol{x}) | \mathrm{Z} = 1] + \mathbb P(\mathrm{Z} = 0) \cdot \mathbb E_{\boldsymbol{x}}[\mathcal{L}\_{\eta}(\alpha, 0) \cdot \eta_{c}(\boldsymbol{x}) | \mathrm{Z} = 0] \\\\
    &= \mathbb P(\mathrm{Z} = 1) \cdot \mathcal{L}\_{\eta}(\alpha, 1) \cdot \mathbb E_{\boldsymbol{x}}[ \boldsymbol{\beta}^T \boldsymbol{x} | \mathrm{Z} = 1] + \mathbb P(\mathrm{Z} = 0) \cdot \mathcal{L}\_{\eta}(\alpha, 0) \cdot \mathbb E_{\boldsymbol{x}}[ \boldsymbol{\beta}^T \boldsymbol{x} | \mathrm{Z} = 0] \\\\
    &= \mathbb P(\mathrm{Z} = 1) \cdot \mathcal{L}\_{\eta}(\alpha, 1) \cdot \boldsymbol{\beta}^T \big ( \mathbb E[ \boldsymbol{x} | \mathrm{Z} = 1] - \mathbb E[ \boldsymbol{x} | \mathrm{Z} = 0] \big ) \tag{Eq. 5} \\\\
    &= \boldsymbol{\beta}^T \boldsymbol{\delta},
    \end{align*}
$$

which contradicts our assumption that $\langle \boldsymbol{\beta}, \boldsymbol{\delta} \rangle > 0$. Therefore $c > 0$.

# Additive concept edits

We define an **additive edit** as a transformation which replaces a feature vector $\boldsymbol{x}$ with $\boldsymbol{x}' = \boldsymbol{x} + a \boldsymbol{u}$ for some unit vector $\boldsymbol{u} \notin \mathrm{span}(\boldsymbol{x})$ and some scalar "intensity" $a \neq 0$. This kind of edit was used by Marks and Tegmark 2023, and the goal is to move the latent prediction in a specified _direction_; that is, to ensure $\tau = \eta(\boldsymbol{x}') - \eta(\boldsymbol{x})$ has the desired sign. We also expect that the magnitude of $\tau$ should monotonically increase with $|a|$.

Since we assume $\eta$ is linear, an additive edit will be successful in this minimal sense if and only if the edit direction is in the half-space of the latent coefficients $\boldsymbol{\beta}$; that is

$$
    \nabla_{\boldsymbol{u}} \eta(\boldsymbol{x}) = \boldsymbol{u}^T \Big(\frac{\partial \eta}{\partial \boldsymbol{x}}\Big) = \boldsymbol{u}^T \boldsymbol{\beta} > 0,
$$

where $\nabla_{\boldsymbol{u}} \eta(\boldsymbol{x})$ denotes the directional derivative of $\eta(\boldsymbol{x})$ along $\boldsymbol{u}$. In general we would like $\nabla_{\boldsymbol{u}} \eta(\boldsymbol{x})$ to be as large as possible, since this achieves a larger effect size $|\tau|$ with a constant-norm change to $\boldsymbol{x}$:

$$
    |\tau| = |\eta(\boldsymbol{x}') - \eta(\boldsymbol{x})| = |\boldsymbol{\beta} (\boldsymbol{x} + a \boldsymbol{u}) - \boldsymbol{\beta} \boldsymbol{x}| = |a \boldsymbol{\beta}^T \boldsymbol{u}| = | a \nabla_{\boldsymbol{u}}\eta(\boldsymbol{x}) |.
$$

By the Cauchy-Schwartz inequality, $|\tau|$ is maximized when $\boldsymbol{u} \in \mathrm{span}(\boldsymbol{\beta})$, so optimal additive editing is trivial when $\boldsymbol{\beta}$ is known.

**Maximin additive edits.** When $\boldsymbol{\beta}$ is unknown, we can successfully perform additive edits by selecting $\boldsymbol{u}$ to maximize the **worst-case** directional derivative.

**Theorem 3.**
Let $\mathrm X$ and $\mathrm{Z}$ be random vectors taking values in $\mathbb{R}^d$ and $\{0, 1\}$ respectively. Let $H$ denote the set of all admissible predictors $\eta : \mathbb{R}^d \rightarrow \mathbb{R}$ for $(\mathrm X, \mathrm{Z})$ of the form $\eta(\boldsymbol{x}) = \boldsymbol{\beta} \boldsymbol{x} + \alpha$. Then the maximin directional derivative objective

$$
    \underset{\| \boldsymbol{u} \| = 1}{\mathrm{argmax}} \inf_{\eta \in H} \nabla_{\boldsymbol{u}} \eta(\boldsymbol{x})
$$

is maximized by the difference-in-means direction $\boldsymbol{u}^* = \frac{\boldsymbol{\delta}}{\| \boldsymbol{\delta} \|}$.

**Proof.** Consider the orthogonal decomposition of $\boldsymbol{\beta}$ into $S = \mathrm{span}(\boldsymbol{\delta})$ and $S^\perp$:

$$
    \nabla_{\boldsymbol{u}} \eta(\boldsymbol{x}) = \boldsymbol{u}^T \boldsymbol{\beta} = \boldsymbol{u}^T (\boldsymbol{\beta}\_S + \boldsymbol{\beta}\_{S^\perp} ) = b \boldsymbol{u}^T \boldsymbol{\delta} + \boldsymbol{u}^T \boldsymbol{\beta}\_{S^\perp},
$$

where $b$ is a positive scalar by Theorem 1. By Cauchy-Schwartz, the first term is maximized when $\boldsymbol{u} = c \boldsymbol{\delta}$ for some $c > 0$, and hence $\boldsymbol{u} \in S$, no matter the value of $\boldsymbol{\beta}$.

Since $\boldsymbol{\beta}\_{S^\perp}$ is free to take any value in $S^\perp$, we cannot lower bound $\boldsymbol{u}^T \boldsymbol{\beta}\_{S^\perp}$ unless $\boldsymbol{u}^T \boldsymbol{v} = 0$ for every $\boldsymbol{v}$ in $S^\perp$. To see this, suppose $\boldsymbol{u}^T \boldsymbol{v} \neq 0$ for some $\boldsymbol{v} \in S^\perp$. Then we can select $\boldsymbol{\beta}$ such that $\boldsymbol{\beta}\_{S^\perp} = \lambda \boldsymbol{v}$ for any arbitrarily large $\lambda \in \mathbb{R}$, with the appropriate sign so that $\boldsymbol{u}^T \boldsymbol{\beta}\_{S^\perp}$ is an arbitrarily large negative value. Hence the second term is maximized when $\boldsymbol{u} \in (S^\perp)^\perp = S$.

Since the optima for the first term are also optima for the second term, _a fortiori_ they are optimal for the original objective. Since we are imposing a unit norm constraint on $\boldsymbol{u}$, we have $\boldsymbol{u}^* = \frac{\boldsymbol{\delta}}{\| \boldsymbol{\delta} \|}$.

# Future work
The above results help explain the success of diff-in-means concept edits in particular. But Marks and Tegmark, as well as our recent paper [Eliciting Latent Knowledge from Quirky Language Models](https://arxiv.org/abs/2312.01037), find that the diff-in-means subspace can also be used to _read out_ concepts from a model's activations in ways that are particulary robust to distribution shifts. In the future, we would like to explore theoretical explanations for this phenomenon as well.

_Thank you to Sam Marks for discussion and feedback on this post, especially regarding Theorem 2._
