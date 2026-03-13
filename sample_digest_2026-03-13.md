# 🗞️ Tech & AI News Digest
*March 13, 2026 — 10 stories*

---

### 1. [Executing programs inside transformers with exponentially faster inference](https://www.percepta.ai/blog/can-llms-be-computers)
*Hacker News*

Researchers at Percepta have announced a significant breakthrough in executing programs inside transformers, resulting in exponentially faster inference times. Christos Tzamos and his team have developed a method that allows transformers, a type of artificial neural network, to directly interpret and execute machine code, bypassing the need for interpretation layers.

This development holds potential practical implications for software engineers and AI researchers, as it could lead to more efficient and faster machine learning models, especially in areas requiring complex computations such as autonomous systems or high-frequency trading.

However, it's essential to note that this research is still in its early stages, and there are several open questions and limitations. For instance, the current approach might struggle with handling certain types of machine code, and the performance gains could vary depending on the specific use case.

Looking ahead, it will be interesting to see how this research evolves and what further optimizations can be made to ensure robust and scalable execution of programs inside transformers.

---

### 2. [Why Your Phone Battery Dies Faster During a Public Emergency](https://www.wired.com/story/why-your-phone-battery-dies-faster-during-a-public-emergency/)
*WIRED*

During public emergencies, phone batteries tend to deplete faster than usual, not primarily due to increased internet usage but rather due to the phone's efforts to maintain a connection when cell towers are damaged or overloaded. The main culprit is the increased activity from the phone's modem, which consumes a significant amount of power, especially when signals are weak or unstable.

Research indicates that network overloading or damage during emergencies worsens signal strength, causing phones to boost transmission power, which in turn drains battery life faster. This increased energy consumption is a result of continuous reconnecting, data transmissions, and the phone's radio and processor staying active for longer periods due to heavy network traffic.

It is essential to note that even when not actively being used, a phone's modem remains active, consuming around 40% of total mobile energy when downloading data. Furthermore, phones often switch between towers or network types to find a better connection, which increases energy consumption due to frequent reconnecting and re-syncing.

In the future, understanding these factors could help developers optimize battery life in mobile devices during emergency situations, improving overall communication efficiency and reliability.

---

### 3. [Y Combinator-backed Random Labs launches Slate V1, claiming the first 'swarm-native' coding agent](https://venturebeat.com/orchestration/y-combinator-backed-random-labs-launches-slate-v1-claiming-the-first-swarm)
*VentureBeat*

In a significant development for the software engineering and AI research communities, Random Labs, a company backed by Y Combinator, has launched Slate V1, which they claim is the first 'swarm-native' coding agent. Slate V1 leverages a distributed computing model to address complex coding tasks as a swarm of individual agents working together.

The technical substance of Slate V1 involves the creation of an intelligent system capable of handling large-scale programming tasks without a central controller. This decentralized approach allows for greater scalability, flexibility, and resilience in tackling diverse programming challenges.

The practical implications for developers and researchers are substantial. Slate V1 has the potential to revolutionize how software is developed and maintained by offering a highly scalable and adaptive solution for coding complex systems. By handling intricate tasks in parallel, it can significantly reduce development time and increase efficiency.

However, it's important to note that while Slate V1 represents a significant step forward in the field of decentralized programming, it's still in its early stages. Users may encounter limitations when working with complex tasks that require nuanced understanding and coordination. Moreover, as the technology matures, it will be interesting to watch how the swarm-native approach evolves and how it compares with traditional centralized systems.

---

### 4. [Anthropic gives Claude shared context across Microsoft Excel and PowerPoint, enabling reusable workflows in multiple applications](https://venturebeat.com/orchestration/anthropic-gives-claude-shared-context-across-microsoft-excel-and-powerpoint)
*VentureBeat*

Anthropic, a leading AI company, has integrated their language model, Claude, with Microsoft's Excel and PowerPoint applications. This integration allows Claude to share context across both platforms, enabling the creation of reusable workflows. Developers can now leverage Claude's capabilities to automate tasks, such as data analysis in Excel and presentation creation in PowerPoint, without having to switch between applications.

For researchers and developers, this development simplifies workflow management and boosts productivity by reducing context switching and manual data transfer between applications. It also opens up new possibilities for building more integrated, versatile AI-powered tools.

However, it's important to note that while this integration offers a more seamless user experience, it raises questions about data privacy and security, as the Claude model will now have access to users' Microsoft data. Additionally, the long-term effects of this integration on the overall user experience and performance of the Microsoft applications are yet to be determined.

Looking ahead, it will be interesting to see how Anthropic continues to develop and expand Claude's capabilities across other popular productivity tools.

---

### 5. [Brutal times for the US battery industry](https://www.technologyreview.com/2026/03/12/1134197/us-battery-industry/)
*MIT Technology Review*

In 2026, the US battery industry is facing a downturn with companies like 24M Technologies, a once-promising startup valued at over $1 billion, shutting down and auctioning off its property. This follows a series of setbacks in the industry, indicating a shift from the boom years when numerous battery startups emerged with innovative chemistries.

The struggles of these companies, including 24M which aimed to improve lithium-ion technology rather than depart from it, suggest a challenge for startups trying to compete with the established lithium-ion batteries that power various devices and electric vehicles. The industry's future now seems uncertain, as investors pull back and startups struggle to succeed.

Looking ahead, it will be interesting to observe how the battery industry adapts, whether through consolidation, changes in strategy, or a continued focus on innovation in an attempt to break away from the lithium-ion dominance. Developers and researchers should keep an eye on industry trends and potential opportunities that may arise from these challenges.

---

### 6. [Hustlers are cashing in on China’s OpenClaw AI craze](https://www.technologyreview.com/2026/03/11/1134179/china-openclaw-gold-rush/)
*MIT Technology Review*

A new open-source AI tool, OpenClaw, has gained significant popularity in China, leading to a burgeoning business opportunity for early adopters like Feng Qingyang. Originally designed to autonomously complete tasks for users, OpenClaw has become so popular that Feng, a software engineer based in Beijing, saw an opportunity to offer installation support as a side gig on Xianyu, a secondhand shopping site. Feng's service, which promises to help non-technical users set up their AI assistant quickly and remotely, has grown into a professional operation with over 100 employees, handling thousands of orders. This trend underscores the growing interest in AI technology among the Chinese public and presents a unique business opportunity for those with the technical skills to facilitate its adoption. It's important to note that as OpenClaw continues to gain traction, potential users should be mindful of the security and privacy implications of such AI tools. Keep an eye on the evolving landscape of OpenClaw and similar AI technologies in China.

---

### 7. [Shopify/liquid: Performance: 53% faster parse+render, 61% fewer allocations](https://simonwillison.net/2026/Mar/13/liquid/#atom-everything)
*Simon Willison's Weblog*

Shopify's CEO, Tobias Lütke, announced a significant performance improvement for the open-source Ruby template engine, Liquid, used in Shopify's platform. Utilizing a variant of Andrej Karpathy's autoresearch system, Lütke found and implemented 93 micro-optimizations over two days, resulting in a 53% faster parse+render speed and a 61% reduction in allocations.

Key changes include replacing StringScanner with String#byteindex for single-byte byteindex searching, which reduced parse time by approximately 12%; employing pure-byte parse_tag_token to eliminate costly StringScanner resets for every {% %} token; and caching small integer to_s, pre-computing frozen strings for 0-999 to avoid 267 Integer#to_s allocations per render.

These improvements matter to developers and researchers because they lead to faster, more efficient code execution, which is essential for maintaining and scaling complex web applications like Shopify's platform. However, it's worth noting that the full impact of these optimizations may not be fully realized until they are tested in real-world scenarios.

Looking ahead, it will be interesting to see how these optimizations perform in practice, and whether they can be applied to other Ruby or web development projects to similarly improve performance.

---

### 8. [Coding After Coders: The End of Computer Programming as We Know It](https://simonwillison.net/2026/Mar/12/coding-after-coders/#atom-everything)
*Simon Willison's Weblog*

In the March 12th article by Clive Thompson for the New York Times Magazine, titled "Coding After Coders: The End of Computer Programming as We Know It," AI-assisted development in the tech industry is highlighted. The article, which features interviews with over 70 software developers from tech giants like Google, Amazon, Microsoft, Apple, and individual experts including Simon Willison, discusses the increasing role of AI in coding.

Willison, a tech entrepreneur and a prominent blogger, explains that while AI might hallucinate, the unique aspect of coding is that developers can test AI-generated code to ensure its accuracy. This has led to optimism among developers about the future of their line of work, with the possibility of increased demand due to the Jevons paradox being mentioned.

However, the article does raise questions about the future implications of AI in programming. A critical voice comes from Willison himself, who suggests that while programming may become easier with AI, other professions like law may face challenges in automating their work without the ability to automatically check for errors or hallucinations.

In the evolving landscape of tech, developers and AI researchers should watch for further developments in AI-assisted coding and consider the potential impact on their fields.

---

### 9. [Sorting algorithms](https://simonwillison.net/2026/Mar/11/sorting-algorithms/#atom-everything)
*Simon Willison's Weblog*

On March 11, 2026, Simon Willison published an article showcasing animated explanations of various sorting algorithms, including bubble sort, selection sort, insertion sort, merge sort, quick sort, heap sort, and Python's Timsort. The demonstrations were built using Claude Artifacts, a tool that allows for interactive animations on mobile devices.

Willison added Python's Timsort to the sequence by cloning a clone of python/cpython from GitHub. However, GPT-5.4 Thinking noted that the code was a simplified, Timsort-inspired adaptive mergesort, indicating potential discrepancies.

The article also introduced a "run all" button, which displays smaller animated charts for each algorithm in a grid and runs them simultaneously. A new color scheme for the buttons was implemented, improving the visual appeal.

This development is significant for developers and AI researchers as it offers an interactive and engaging way to understand and compare different sorting algorithms, which are fundamental concepts in computer science and software engineering. It also showcases the growing capabilities of AI and machine learning tools in automating complex tasks, such as cloning repositories from GitHub.

However, it is crucial to be aware of the potential differences between the implemented Timsort algorithm and the original one, as highlighted by GPT-5.4 Thinking. Future developments may focus on refining the AI's ability to accurately replicate and understand complex algorithms like Timsort.

---

### 10. [Plan mode is now available in Gemini CLI](https://developers.googleblog.com/plan-mode-now-available-in-gemini-cli/)
*Google Developers Blog*

Gemini CLI has introduced a new feature, Plan mode, which enables the tool to analyze requests, plan complex changes, understand code bases or dependencies, and propose strategies for review, all without risk of accidental modifications. In Plan mode, Gemini CLI can navigate your codebase, search for patterns, read documentation, and use tools like `read_file`, `grep_search`, `glob`, `codebase_investigator`, and `Agent Skills` to understand complex system dependencies and workflows. However, it cannot modify any files except for its own internal plans.

To ensure the proposed plan aligns with your intentions, Gemini CLI now includes the `ask_user` tool, allowing it to pause its research and ask targeted questions to clarify your goals or gather missing information. This bidirectional communication ensures that the agent can present options, request clarification on specific architectural choices, or ask for the location of hidden configuration files.

For developers and AI researchers, this feature provides a safer way to explore complex changes or new features without the risk of unintended modifications to the codebase. By using Plan mode, you can validate assumptions, understand dependencies, and gather necessary information to make informed decisions about your projects.

It's essential to note that a plan's effectiveness depends on the accuracy of the information provided during the questioning phase. Additionally, Plan mode restricts Gemini CLI to a subset of its tools, and the agent cannot execute any changes until you explicitly exit Plan mode using the `exit_plan_mode` tool.

In the future, it will be interesting to see how Gemini CLI continues to evolve and integrate more advanced AI capabilities to further assist developers and researchers in their projects.

---

### ⚠️ Failed sources
- https://openai.com/news/rss/
- https://www.anthropic.com/rss.xml