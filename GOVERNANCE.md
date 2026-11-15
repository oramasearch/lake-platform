# Governance

How Orama Lake is run: who decides what, how someone becomes a maintainer, and what Orama keeps.

Orama Lake is led by Orama Search Inc. ("Orama"), which wrote most of it and runs it as a hosted
service. Decisions are made in public, by the maintainers of each component, and anyone can become one.

## The code stays MIT

The code Orama Lake releases is under the [MIT license](LICENSE), and it stays under it. There is no
enterprise edition of the code and no feature held back for paying customers.

Contributions come in under the [Developer Certificate of Origin](https://developercertificate.org/)
(a `Signed-off-by` line on each commit), with no contributor license agreement. So each contribution
keeps the license it came in with, and Orama could not relicense other people's work even if it
wanted to. That is on purpose.

Forks of third-party code that the stack carries keep their upstream licenses. Model weights carry the
license stated beside them.

## Roles

| Role | Can | Becomes one by |
|---|---|---|
| **Contributor** | Open issues, pull requests and RFCs; answer questions; review | Taking part |
| **Triager** | Label, reproduce and close issues; mark answers in Discussions | Steady, accurate help in issues or Q&A, invited by a maintainer |
| **Reviewer** | Review pull requests in one component; their approval counts toward a merge | Sustained, good contributions and reviews in that component, proposed by a maintainer of it |
| **Maintainer** | Merge, cut releases and decide RFCs for their component | Sustained reviewing, nominated by a maintainer, a majority vote of that component's maintainers, and no objection from the project lead within seven days |
| **Project lead** | Sets the roadmap across components, breaks ties, and holds what Orama keeps (below) | Orama |

The maintainers of each component are listed in `MAINTAINERS.md`, one section per component. A
maintainer who has not reviewed or merged anything for six months moves to emeritus, with thanks, and
can come back by asking.

## How decisions are made

- **Day to day:** in public, on the issue or the pull request. A change merges with the approval of a
  maintainer of that component, who is not its author.
- **When maintainers disagree:** the component's maintainers decide by majority, and the project lead
  breaks a tie. The reasons are written on the issue or the RFC.
- **Larger changes go through an RFC** (below).
- **The roadmap** is [`ROADMAP.md`](ROADMAP.md), changed by pull request like everything else.
- **This document** is changed by an RFC, decided by the project lead with the maintainers.

## RFCs

An RFC is needed for a new product surface, a change to a public API, protocol or file format, a new
dependency of a whole component, or a change to this document. Open it as a discussion in the RFC
category, with:

1. the problem, and who has it;
2. the proposal;
3. the alternatives considered;
4. what it breaks, and how users move;
5. how it is tested.

It stays open for comment for at least fourteen days. The maintainers of the components it touches
decide, and write down why. An accepted RFC becomes issues; a declined one stays visible with its
reason.

## What Orama keeps

Said plainly, so there is no surprise later:

- **The names and logos.** "Orama", "Orama Lake" and the component names and logos are trademarks of
  Orama Search Inc. The code is MIT; the names are not. A fork can do anything the license allows with
  the code, and picks its own name. See [`TRADEMARKS.md`](TRADEMARKS.md).
- **The security process.** Vulnerabilities are reported privately to `security@orama.com`
  ([`SECURITY.md`](SECURITY.md)), and fixes are released before details are public.
- **The release keys.** Orama signs the releases. Anyone can check a signature; only the release
  process can make one.
- **The project lead's tie-break and the cross-component roadmap**, until the project has a broader
  home (below).

## Orama's business

Orama earns on what goes on top of the free stack: running it for you as a hosted service, engineers
who build with your team, enterprise support with an SLA, and a marketplace for what people build on
the stack. None of it is a part of the code that is held back. Paid support is never pushed in the
community's help channels.

## A broader home later

The project starts Orama-led, the way most projects of its kind have. Whether it later moves to a
neutral foundation will be decided in public, by an RFC, once there are maintainers from several
organizations and the project's users ask for it. Nothing in this document stops that.

## Conduct

Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md). Reports go to
`conduct@orama.com` and are handled privately by the moderators; a moderator involved in a report
steps aside.
