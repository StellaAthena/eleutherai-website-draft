---
title: "Free Form Least-Squares Concept Erasure Without Oracle Concept Labels"
date: 2024-06-13T16:00:00-00:00
description: "Achieving even more surgical edits than LEACE without concept labels at inference time."
author: ["Brennan Dury", "Nora Belrose"]
ShowToc: true
mathjax: true
draft: false
---

_This post assumes some familiarity with the idea of concept erasure and our LEACE concept erasure method. We encourage the reader to consult our [arXiv paper](https://arxiv.org/abs/2306.03819) for background._

In our paper [LEACE: Perfect linear concept erasure in closed form](https://arxiv.org/abs/2306.03819), we derived a concept erasure method that is least squares optimal within the class of affine transformations. We now extend this result by deriving the least squares optimal edit only under the restriction that the edited representation is a function of the unedited representation.

In a previous [blog post](https://blog.eleuther.ai/oracle-leace/), we solved this problem in the case where the transformation may depend both on the representation $\mathbf x$ and the label $\mathbf z$. This assumption allows a more surgical edit than the edit found here, but requires access to labels at inference time and comes at the cost of possibly injecting non-linearly represented information into the representation, as discussed in the blog post. By not assuming access to labels, we solve both issues.

In Theorem 1 below, we derive **Free Form LEACE** ("FF-LEACE"), a closed-form formula for the function $r : \mathbb{R}^n \rightarrow \mathbb{R}^n$ nearest to the identity function such that no linear classifier can do better than chance at predicting $\mathrm Z$ from $\mathrm r(X)$, or equivalently $\mathrm{Cov}(\mathrm r(X), \mathrm Z) = \textbf{0}$.

## Derivation

We prove a more general result, where we are interested in the case $\Omega = \mathbb{R}^n$ and $h(x) = x$.

**Theorem 1.**

Let $X$ be a random object taking values in the set $\Omega$, and let $Z$ be a random vector in $\mathbb{R}^k$. Let $h: \Omega \rightarrow \mathbb{R}^n$ be measurable and define $f : \Omega \rightarrow \mathbb{R}^k$ such that $f(x) = \mathbb{E}[Z | X=x]$. Assume $h(X)$ and $f(X)$ have finite second moments. Then for every p.s.d. inner product $\langle \mathbf a, \mathbf b \rangle\_{\mathbf M} = \mathbf a^T \mathbf M \mathbf b$ on $\mathbb{R}^d$, the objective

$$
    \mathop{\mathrm{inf \hspace{0.5em}}}\_{\substack{\mathrm r : \Omega \rightarrow \mathbb{R}^n}} \mathbb{E} \big\| \mathrm r(X) - \mathrm h(X) \big\|^2\_{\mathbf M} \quad \mathrm{s.t.} \hspace{0.5em} \mathrm{Cov}(\mathrm r(X), \mathrm Z) = \mathbf{0}
$$

is minimized by:

$$
    r^*(x) = h(x) - \mathbf{\Sigma}\_{h(X)Z} \mathbf{\Sigma}\_{f(X)f(X)}^+ \big(\mathrm f(x) - \mathbb{E}[\mathrm Z]\big)
$$

where $\mathbf{A}^{+}$ denotes the Moore-Penrose pseudoinverse of a matrix $\mathbf{A}$.

**Proof.**

Observe that $\mathrm{Cov}(r(X), Z) = \mathrm{Cov}(r(X), f(X))$, so we rewrite the objective as:

$$
    P\_1 = \mathop{\mathrm{inf \hspace{0.5em}}}\_{\substack{\mathrm r : \Omega \rightarrow \mathbb{R}^n}} \mathbb{E} \big\| \mathrm r(X) - \mathrm h(X) \big\|^2\_{\mathbf M} \quad \mathrm{s.t.} \hspace{0.5em} \mathrm{Cov}(\mathrm r(X), \mathrm f(X)) = \mathbf{0}
$$

We first consider a related objective. Let $\mathcal H$ be the Hilbert space of square-integrable real-valued random variables equipped with the inner product $\langle \xi, \zeta \rangle\_{\mathcal H} := \mathbb{E}[\xi \zeta]$. Now consider:

$$
    P\_2 = \mathop{\mathrm{inf \hspace{0.5em}}}\_{\substack{\mathrm Y \in \mathcal H}^n} \mathbb{E} \big\| \mathrm Y - \mathrm h(X) \big\|^2\_{\mathbf M} \quad \mathrm{s.t.} \hspace{0.5em} \mathrm{Cov}(\mathrm Y, \mathrm f(X)) = \mathbf{0}
$$

Any function $r : \Omega \rightarrow \mathbb{R}^n$ that is feasible for $P\_1$ corresponds to a random variable $r(X)$ that is feasible for $P\_2$. So $P\_2 \leq P\_1$.

By assumption, $h(X)$ and $f(X)$ have finite second moments, so $h(X) \in \mathcal{H}^n$ and $f(X) \in \mathcal{H}^k$. So, we showed in the previous [blog post](https://blog.eleuther.ai/oracle-leace/) that $P\_2$ is minimized by the (appropriately shifted) ordinary least squares residuals from regressing $\mathrm h(X)$ on $\mathrm f(X)$:

$$
    \mathrm Y\_{\mathrm{LEACE}} = \mathrm h(X) - \mathbf{\Sigma}\_{h(X)f(X)} \mathbf{\Sigma}\_{f(X)f(X)}^+ \big(\mathrm f(X) - \mathbb{E}[\mathrm f(X)]\big)
$$

Notice that $Y\_{\mathrm{LEACE}} = r^\*(X)$, where $r^\* : \Omega \rightarrow \mathbb{R}^n$ is such that $r^\*(x) = h(x) - \mathbf{\Sigma}\_{h(X)f(X)} \mathbf{\Sigma}\_{f(X)f(X)}^+ \big(\mathrm f(x) - \mathbb{E}[\mathrm f(X)]\big)$. Since $r^*$ is feasible for $P\_1$ and $Y\_{\mathrm{LEACE}}$ is optimal for $P\_2$, $P\_1 \leq P\_2$.

So $P\_1 = P\_2$, with minimizer $r^\*$. Since $E[f(X)] = \mathbb{E}[Z]$ and $\mathbf{\Sigma}\_{h(X)f(X)} = \mathbf{\Sigma}\_{h(X)Z}$, we rewrite $r^*(x) = h(x) - \mathbf{\Sigma}\_{h(X)Z} \mathbf{\Sigma}\_{f(X)f(X)}^+ \big(\mathrm f(x) - \mathbb{E}[\mathrm Z]\big)$.

## Discussion

The main difficulty of applying FF-LEACE is that we need to estimate the conditional expectation $f(x) = \mathbb{E}[Z | X=x]$. This is a non-trivial problem, especially in high dimensions. However, if we have access to a large dataset, we might be able to estimate $f(x)$ using a neural network. We could then apply FF-LEACE using the learned function.

You can find a PyTorch implementation of FF-LEACE in our [GitHub repository](https://github.com/EleutherAI/concept-erasure/blob/main/experiments/fleace.py). There, we apply it to a toy problem where the conditional expectation can be computed in closed form.