# PRG455 Event Driven Programming for Embedded Systems (M5Stack Core S3 / MicroPython)

## Course Description

This course bridges high-level application development with embedded systems. Students build
professional-grade, touch-driven graphical interfaces that run directly on the M5Stack Core S3
(an ESP32-S3-based microcontroller), using MicroPython and M5Stack's M5UI graphical widget
library. The course emphasizes AI-assisted orchestration, where students use LLMs to generate
boilerplate code and troubleshoot hardware-specific behaviour, focusing their own effort on
system architecture, data integrity, interface design, and hardware-software integration.

Interfaces are built entirely from a defined set of GUI controls — labels, buttons, bars,
switches, sliders, spinboxes, dropdowns, images, and LED indicators — deliberately excluding free
text entry, since the device's on-screen keyboard is not reliable enough for graded work. Each
lab pairs one of these controls with a distinct piece of Core S3 hardware (touch, motion sensing,
camera, microphone, speaker, and wireless connectivity), building toward a final project that
integrates several of these capabilities into a single application.

## Credit Status

One subject credit in the Computer Engineering Technology program.

## Prerequisite(s)

PRG355

## Topic Outline (week by week)

| Week | Lecture Topic | Lab Activity |
|---|---|---|
| 1 | Course introduction. Development environment setup: GitHub (using GitHub Desktop), Visual Studio Code, and Claude Pro integration within VS Code. | Lab 1: Create GitHub repositories for the course; connect Claude Pro to VS Code; first AI-assisted commit. |
| 2 | MicroPython and the Core S3: flashing UIFlow2 firmware, connecting via the UIFlow2 web editor, and running code with Run Once. | Lab 2: Flash the course-standard firmware; verify serial output, display output, and a basic sensor read. |
| 3 | Basic GUI widgets and touch input: Label, Button, and Slider. | Lab 3: Local AI GPU Advisor — slider-driven parameter selection with formula-based output. |
| 4 | Motion sensing and the IMU: Bar and Switch widgets. | Lab 4: An IMU-driven interface using a bar display and a mode switch. |
| 5 | The camera and visual feedback: the Image widget. | Lab 5: A camera-driven interface displaying captured or live image data. |
| 6 | Cumulative review: GUI construction, event handling, and widget-driven logic (Weeks 1–5). | Lab Test 1 — GUI & Logic Fundamentals. |
| 7 | Audio input and the microphone: the LED widget. | Lab 6: A microphone-driven interface using an LED indicator. |
| 8 | Audio output and the speaker: the Spinbox widget. | Lab 7: A speaker-driven interface using a spinbox control. |
| 9 | Wireless connectivity: Wi-Fi on the Core S3, and the Dropdown widget. | Lab 8: A connectivity-driven interface using a dropdown control. |
| 10 | Major project: design, architecture, and AI-assisted planning. | Project work time: proposal and design review. |
| 11 | Major project: implementation, integration, and AI-assisted debugging. | Project work time: implementation. |
| 12 | Cumulative review: hardware/software integration across the full widget and sensor set. | Lab Test 2 — Hardware/Software Integration. Major Project due. |
| 13 | Course wrap-up and synthesis. | Major Project presentations. |

## Evaluation

| Component | Weight |
|---|---|
| Lab Assignments (8) | 36% (approx. 4.5% each) |
| Lab Test 1 (Week 6) — GUI & Logic Fundamentals | 22% |
| Lab Test 2 (Week 12) — Hardware/Software Integration | 22% |
| Major Project (Due Week 12) | 20% |
| **Total** | **100%** |

## AI Collaboration Policy

Students are encouraged to use LLMs as a "Pair Programmer" to assist with Python syntax and to
accelerate development. Evaluation focuses on the student's ability to integrate AI-generated
logic and ensure the functional requirements of the code are met on the actual Core S3 hardware
— not on the ability to write MicroPython or M5UI syntax from memory.

Students are required to submit a **Prompt Appendix** for all evaluations, documenting their
AI-assisted workflow. In practice, this is maintained as a `PROMPTS.md` file committed alongside
the code in the relevant GitHub repository, logging what was asked of the AI tool and what was
used from its response. This shifts the assessment focus from rote memorization to system
behaviour, integration, and the student's judgment in verifying and adapting AI output — since a
plausible-looking answer is not the same as one confirmed correct on real hardware.

## Learning Outcomes

Upon successful completion of this subject the student will be able to:

1. Build and run touch-driven graphical interfaces on the M5Stack Core S3 using MicroPython and
   the M5UI widget library, focusing on event-driven architectures that respond to user and
   hardware input.

2. Design functional user interfaces using the course's defined set of M5UI controls (labels,
   buttons, bars, switches, sliders, spinboxes, dropdowns, images, and LED indicators), and
   implement event-driven callbacks to manage application state.

3. Structure event-driven MicroPython programs using functions, event handler dispatch, and
   closures to encapsulate reusable widget behaviour, maintaining clear separation between
   application state, hardware setup, and event handling logic.

4. Architect robust applications that manage local and global scope effectively, ensuring
   application stability across the device's power and connection lifecycle.

5. Develop applications that read from and respond to the Core S3's onboard sensors — touch,
   IMU, camera, microphone — and its onboard actuators, including the speaker, integrating sensor
   data directly into the graphical interface.

6. Implement effective error handling for hardware-facing code, accounting for firmware and
   library variation, sensor read failures, and invalid or out-of-range widget state.

7. Utilize Generative AI (LLMs) as a development partner to assist in code generation, API
   verification, and debugging, while maintaining academic integrity through documented prompt
   strategies.

8. Understand and make effective use of the GitHub platform, via the GitHub Desktop application,
   to maintain version-controlled snapshots of all lab, lab test, and project work.

9. Integrate AI tools within the Visual Studio Code platform, use Markdown files to structure and
   improve AI-assisted workflows, and access AI tools from the command line.

## Essential Employability Skills

**A)** Execute mathematical operations accurately: Apply algebraic and trigonometric principles
to scale, calibrate, and interpret raw sensor data from embedded microcontrollers.

**B)** Apply a systematic approach to solve problems: Utilize structured debugging techniques to
isolate hardware behaviour issues and software logic errors in complex, event-driven system
architectures.

**C)** Use a variety of thinking skills to anticipate and solve problems: Evaluate the trade-offs
between AI-generated solutions and manual coding to optimize for system performance, reliability,
and code maintainability.

**D)** Locate, select, organize, and document information using appropriate technology and
information systems: effectively utilize Generative AI tools and version control systems to
manage, document, and iterate on code and project prompts.

**E)** Analyze, evaluate, and apply relevant information from a variety of sources: Critically
verify the logic and correctness of code sourced from LLMs, technical documentation, and online
repositories before integration into hardware systems.

**F)** Manage the use of time and other resources to complete projects: Prioritize development
tasks by balancing hardware-software integration requirements against strict project timelines
and lab test milestones.

**G)** Demonstrate digital literacy and ethical AI use: Apply ethical standards when using AI
assistants, ensuring transparency in code attribution and acknowledging the limitations of
machine-generated outputs in technical applications.

**H)** Integrate modern development tools and AI assistance to engineer efficient
hardware-software interfaces: Proficiency in utilizing lightweight Integrated Development
Environments (IDEs) like VS Code and leveraging Generative AI as a collaborative partner to
design, write, debug, and optimize code that interacts correctly and efficiently with the Core
S3's onboard hardware.

## Mode of Instruction

Lecture hours: 2
Lab hours: 2

## Prescribed Texts

None. Searches and queries will be obtained via AI.

## Reference Material

None. Searches and queries will be obtained via AI.

## Hardware and Software Requirements

M5Stack Core S3 microcontroller and a monthly paid Claude Pro account.

## Student Progression and Promotion Policy

<a href="http://www.senecapolytechnic.ca/about/policies/student-progression-and-promotion-policy.html" target="_blank" rel="noopener">http://www.senecapolytechnic.ca/about/policies/student-progression-and-promotion-policy.html</a>

## Grading Policy

<a href="http://www.senecapolytechnic.ca/about/policies/grading-policy.html" target="_blank" rel="noopener">http://www.senecapolytechnic.ca/about/policies/grading-policy.html</a>

| Grade | Range |
|---|---|
| A+ | 90% to 100% |
| A | 80% to 89% |
| B+ | 75% to 79% |
| B | 70% to 74% |
| C+ | 65% to 69% |
| C | 60% to 64% |
| D+ | 55% to 59% |
| D | 50% to 54% |
| F | 0% to 49% (Not a Pass) |

**OR**

| Grade | Meaning |
|---|---|
| EXC | Excellent |
| SAT | Satisfactory |
| UNSAT | Unsatisfactory |

For further information, see a copy of the Academic Policy, available online
(<a href="http://www.senecapolytechnic.ca/about/policies/academics-and-student-services.html" target="_blank" rel="noopener">http://www.senecapolytechnic.ca/about/policies/academics-and-student-services.html</a>)
or at Seneca's Registrar's Offices
(<a href="https://www.senecapolytechnic.ca/registrar.html" target="_blank" rel="noopener">https://www.senecapolytechnic.ca/registrar.html</a>).
