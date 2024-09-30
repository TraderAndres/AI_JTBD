# prompt_builder.py
import os
import re
import yaml

class PromptBuilder:

    # Phase 1 prompts (Industry down to High Level Job)
    def build_sectors_prompt(self, industry, fidelity):
        prompt = (
            f"Act as an expert in industry classification. Within the {industry} industry, create a {fidelity} "
            f"list of all the related sectors and include a brief description. For example, within the "
            f"**Agriculture, Forestry, Fishing, and Hunting industry**, one such sector might be "
            f"**Animal Production and Aquaculture**. The strucmture of your response should be as follows:\n\n"
            f"1. **Animal Production and Aquaculture**: This covers livestock farming, dairy production, "
            f"poultry and egg production, and aquaculture.\n\n"
            f"Do not output anything before, or after the list.\n\n"
            f"Always output in markdown.\n\n"
            f"industry: {industry}\n"
            f"fidelity: {fidelity}"
        )
        return prompt

    def build_subsectors_prompt(self, industry, sector, fidelity):
        prompt = (
            f"Act as an expert in industry classification. Within the {industry} industry, and then within the "
            f"{sector} sector, create a {fidelity} list of related subsectors (or all types of products the "
            f"sector produces) and include a brief description. For example, within the "
            f"**Agriculture, Forestry, Fishing, and Hunting industry**, and then within the "
            f"**Animal Production and Aquaculture** sector, one such subsector might be "
            f"**Dairy Cattle and Milk Production**. The structure of your response should be as follows:\n\n"
            f"1. **Dairy Cattle and Milk Production**: This involves raising cattle for milk and dairy products.\n\n"
            f"Do not output anything before, or after the list.\n\n"
            f"Always output in markdown.\n\n"
            f"industry: {industry}\n"
            f"sector: {sector}\n"
            f"fidelity: {fidelity}"
        )
        return prompt

    def build_end_users_provider_prompt(self, industry, sector, subsector, n, fidelity):
        prompt = (
            f"Act as an expert in industry classification. Within the {industry} industry, and then within the "
            f"{sector} sector, and then within the {subsector} subsector, create a {fidelity} list of {n} "
            f"related roles that support the work (or service) and include a brief description. For example, "
            f"within the **Agriculture, Forestry, Fishing, and Hunting industry**, and then within the "
            f"**Animal Production and Aquaculture** sector, and then within the **Dairy Cattle and Milk Production** "
            f"subsector the role might be **Dairy Farmer**. The structure of your response should be as follows:\n\n"
            f"1. **Role**: This is where you describe the role.\n\n"
            f"Do not output anything before, or after the list.\n\n"
            f"Do theme-up customer types if “n” is small, and break them down when “n” is larger.\n\n"
            f"Always output in markdown.\n\n"
            f"industry: {industry}\n"
            f"sector: {sector}\n"
            f"subsector: {subsector}\n"
            f"n: {n}\n"
            f"fidelity: {fidelity}"
        )
        return prompt

    def build_jobs_prompt(self, end_user, industry, sector, subsector, n):
        prompt = (
            f"Act as a(n) {end_user} who works in the {industry} industry with a specialty focus in the "
            f"{sector} sector and {subsector} subsector. I do not want to know what {end_user}s are doing in the "
            f"industry, sector, and/or subsector. I want to know what they could be ultimately trying to accomplish "
            f"in the industry | sector | subsector given their role. What they are trying to accomplish should be "
            f"aligned with desired customer outcomes, not company outcomes.\n\n"
            f"If the industry is healthcare, and the sector is Hospitals, I don’t want to know that they “process patients.” "
            f"I want to know that the are “offering emergency services.”\n\n"
            f"If the industry is construction I don't want to know that they are fastening two pieces of wood together, "
            f"I want to know what they are trying to build.\n\n"
            f"If the industry is a consulting, I don't want to know that they are doing projects, I want to know that they "
            f"are helping a client develop a growth strategy.\n\n"
            f"We're going to call what they are trying to accomplish \"Jobs-to-be-Done.\"\n\n"
            f"I'd like you to generate a list of {n} jobs that the {end_user} is trying to get done.\n\n"
            f"These should be core to the existence of the industry and/or sector. I don’t want to know about one-offs, "
            f"or ad-hoc jobs.\n\n"
            f"A job statement should begin with a verb ending in \"ing\" (the gerund form of a verb).\n\n"
            f"Do not use general terms that do not have a discrete output, like \"Managing\" at the beginning of the job statement.\n\n"
            f"The following is a non-exhaustive list of common verbs that might be used at the beginning of each functional job. "
            f"Allocate 80% of the output to these:\n\n"
            f"1. Achieving\n"
            f"2. Allowing\n"
            f"3. Confirming\n"
            f"4. Coordinating\n"
            f"5. Correcting\n"
            f"6. Creating\n"
            f"7. Demonstrating\n"
            f"8. Detecting\n"
            f"9. Determining\n"
            f"10. Developing\n"
            f"11. Discovering\n"
            f"12. Ensuring\n"
            f"13. Experiencing\n"
            f"14. Finding\n"
            f"15. Fixing\n"
            f"16. Getting\n"
            f"17. Helping\n"
            f"18. Identifying\n"
            f"19. Improving\n"
            f"20. Keeping\n"
            f"21. Learning\n"
            f"22. Locating\n"
            f"23. Maintaining\n"
            f"24. Making\n"
            f"25. Obtaining\n"
            f"26. Planning\n"
            f"27. Preparing\n"
            f"28. Preventing\n"
            f"29. Protecting\n"
            f"30. Providing\n"
            f"31. Relieving\n"
            f"32. Remembering\n"
            f"33. Removing\n"
            f"34. Sharing\n"
            f"35. Staying\n"
            f"36. Stopping\n"
            f"37. Teaching\n"
            f"38. Understanding\n"
            f"39. Updating\n"
            f"40. Verifying\n\n"
            f"Output as a numbered list.\n"
            f"Output the job name in bold.\n"
            f"Explain each job step-by-step after a hyphen.\n"
            f"Do not generate a sentence before the list.\n"
            f"Do not generate anything after the list.\n\n"
            f"Example Format:\n"
            f"1. **Searing Meat** - The ability to create a caramelized crust on the exterior of a meat cut by applying high heat quickly. "
            f"This process enhances the flavor and appearance of the meat, making it more appetizing and palatable.\n\n"
            f"Do theme-up provider jobs if “n” (the number of jobs) is small, and break them down when “n” is larger.\n\n"
            f"Always output in markdown.\n\n"
            f"End user: {end_user}\n"
            f"industry: {industry}\n"
            f"sector: {sector}\n"
            f"subsector: {subsector}\n"
            f"n: {n}"
        )
        return prompt

    def build_end_users_customer_prompt(self, industry, sector_info, subsector_info, n, fidelity):
        prompt = (
            f"Act as an expert in industry classification. Within the {industry} industry, and then within the "
            f"{sector_info} sector, and then within the {subsector_info} subsector, create a {fidelity} list of {n} "
            f"related end user (people who purchase sector products and services) roles that benefit from related solutions "
            f"and include a brief description. For example, within the **Cloud Computing Services industry**, and then within the "
            f"**Software as a Service (SaaS)** sector, and then within the **Customer Relationship Management (CRM) Software** subsector "
            f"the role might be **Marketing Analyst**. In the **Plumbing, Heating, and Air-Conditioning** sector, the role might be a home owner. "
            f"The structure of your response should be as follows:\n\n"
            f"1. **Role**: This is where you describe the role.\n\n"
            f"Do not output anything before, or after the list.\n\n"
            f"Do theme-up customer types if “n” is small, and break them down when “n” is larger.\n\n"
            f"Always output in markdown.\n\n"
            f"industry: {industry}\n"
            f"sector: {sector_info}\n"
            f"subsector: {subsector_info}\n"
            f"n: {n}\n"
            f"fidelity: {fidelity}"
        )
        return prompt

    def build_jtbd_customers_prompt(self, end_user, industry, sector_info, subsector_info, n):
        prompt = (
            f"Act as a(n) {end_user} who works in the {industry} industry with a specialty focus in the "
            f"{sector_info} sector and {subsector_info} subsector. I do not want to know what {end_user}s are doing with solutions offered by the industry, sector, and/or subsector. "
            f"I want to know what they could be ultimately trying to accomplish by using the solutions offered by the industry | sector | subsector given their role as a(n) {end_user}. "
            f"What are they trying to accomplish should be aligned with their desired outcomes, not the outcomes of the company offering the solution.\n\n"
            f"If the industry is Cloud Computing Services, the sector is Software as a Service (SaaS), and the subsector is Customer Relationship Management (CRM) Software, "
            f"I don’t want to know that a Marketing Manager “launches marketing campaigns.” I want to know that they are “developing qualified leads.”\n\n"
            f"We're going to call what they are trying to accomplish \"Jobs-to-be-Done.\"\n\n"
            f"I'd like you to generate a list of {n} jobs that the {end_user} is trying to get done.\n\n"
            f"These should be tightly tied to the solutions offered by the industry and/or sector and/or subsector. I don’t want to know about one-offs, or ad-hoc jobs.\n\n"
            f"A job statement should begin with a verb ending in \"ing\" (the gerund form of a verb).\n\n"
            f"Do not use general terms that do not have a discrete, tangible output at the beginning of the job statement. An example of such a verb that should never be used is \"Managing.\"\n\n"
            f"The following is a non-exhaustive list of common verbs that might be used at the beginning of each functional job. "
            f"Allocate 80% of the output to these:\n\n"
            f"1. Achieving\n"
            f"2. Allowing\n"
            f"3. Confirming\n"
            f"4. Coordinating\n"
            f"5. Correcting\n"
            f"6. Creating\n"
            f"7. Demonstrating\n"
            f"8. Detecting\n"
            f"9. Determining\n"
            f"10. Developing\n"
            f"11. Discovering\n"
            f"12. Ensuring\n"
            f"13. Experiencing\n"
            f"14. Finding\n"
            f"15. Fixing\n"
            f"16. Getting\n"
            f"17. Helping\n"
            f"18. Identifying\n"
            f"19. Improving\n"
            f"20. Keeping\n"
            f"21. Learning\n"
            f"22. Locating\n"
            f"23. Maintaining\n"
            f"24. Making\n"
            f"25. Obtaining\n"
            f"26. Planning\n"
            f"27. Preparing\n"
            f"28. Preventing\n"
            f"29. Protecting\n"
            f"30. Providing\n"
            f"31. Relieving\n"
            f"32. Remembering\n"
            f"33. Removing\n"
            f"34. Sharing\n"
            f"35. Staying\n"
            f"36. Stopping\n"
            f"37. Teaching\n"
            f"38. Understanding\n"
            f"39. Updating\n"
            f"40. Verifying\n\n"
            f"Output as a numbered list.\n"
            f"Output the job name in bold.\n"
            f"Explain each job step-by-step after a hyphen.\n"
            f"Do not generate a sentence before the list.\n"
            f"Do not generate anything after the list.\n\n"
            f"Example Format:\n"
            f"1. **Searing Meat** - The ability to create a caramelized crust on the exterior of a meat cut by applying high heat quickly. "
            f"This process enhances the flavor and appearance of the meat, making it more appetizing and palatable.\n\n"
            f"Do theme-up customer jobs if “n” (the number of jobs) is small, and break them down when “n” is larger.\n\n"
            f"Always output in markdown.\n\n"
            f"End user: {end_user}\n"
            f"Industry: {industry}\n"
            f"Sector: {sector_info}\n"
            f"Subsector: {subsector_info}\n"
            f"n: {n}"
        )
        return prompt


    # Phase 2 prompts (Job down to desired outcomes)
    def build_job_contexts_prompt(self, end_user, job, context, n):
        """
        Constructs the prompt for generating Job Contexts.
        """
        prompt = f"""
        Act as a(n) {end_user} who is {job}. List {n} contexts in which you could be {job}.

        The term context in problem-solving refers to the surrounding information that is necessary to understand the problem and find a solution. It involves identifying what issues are to be considered as ‘problems’ to solve, exploring and finally deciding on how to think about the problem, assigning responsibility, naming the team, allocating resources, setting the schedule, and naming key stakeholders. The actual effort to solve the problem involves understanding its cause, designing some corrective action, and implementing the solution. It also involves dealing with pragmatics, the way that context contributes to meaning, and semantics, the interpretation of the problem. Observing what is going on in your environment; identifying things that could be changed or improved; diagnosing why the current state is the way it is and the factors and forces that influence it; developing approaches and alternatives to influence change; making decisions about which alternative to select; taking action to implement the changes; and observing impact of those actions in the environment.

        Explain each context. Output the context name in bold. Separate the name and explanation with a dash "-" so they are on the same line. Output as a numbered list.

        Always output in markdown.

        Use the following example format for the output:

        1. **IT Managed Services Provider** - A company looking to outsource the management of their IT infrastructure. This often includes network management, security, and data storage solutions.
        End user: {end_user}
        Job: {job}
        n: {n}
        """
        return prompt

    def parse_job_contexts(self, response):
        """
        Parses the response from the LLM into a list of job contexts.
        """
        contexts = []
        lines = response.strip().split('\n')
        pattern = re.compile(r'^\d+\.\s*\*\*(.+?)\*\*\s*-\s*(.+)$')
        for line in lines:
            match = pattern.match(line)
            if match:
                context_name = match.group(1).strip()
                explanation = match.group(2).strip()
                contexts.append({"context_name": context_name, "explanation": explanation})
        return contexts

    def build_job_map_prompt(self, end_user, job, context, fidelity):
        """
        Constructs the prompt for generating the Job Map.
        """
        prompt = f"""
        Act as a(n) {end_user} with a deep expertise in Jobs-to-be-Done theory, which you will use here. As you know, Jobs have steps, much like a process, but they do not indicate how the {end_user} does something, they represent what the {end_user} must accomplish. Also, steps fall under 9 main phases. These phases are sequential. Each of the phases are explained below.

        Explanation of Phases:

        Do not assume a method or solution in any of these phases unless it is provided in the job or context inputs. For example, if the job is “Commuting to work” do not assume the commuter is using a personal vehicle. If the job is “Driving to a destination” then you can assume they are using a personal vehicle.

        1. **Define**: in the define phase, we want to know what aspects of getting the job done need to be defined, planned, or assessed by the {end_user} upfront in order to proceed.

        1. Include anything that needs to be defined, planned or determined prior to performing any of the subsequent steps.

        2. If I’m driving a car to a destination, I might need to determine where I am going, where I can park, assess traffic conditions, and/or determine the available route options

        2. **Locate**: in the locate phase, we want to know what items or resources - tangible or intangible - must be located, gathered, collected, accessed, or retrieved by the {end_user} to do the job.

        1. Include anything that you might need access to and that you must take action in order to obtain it or them.

        2. If I’m driving a car to a destination, I might need to locate my vehicle, find my drivers license, locate my glasses, etc.

        3. **Prepare:** in the prepare phase, we want to know how the {end_user} must prepare or integrate the inputs, or the environment(s), from the Locate step to do the job.

        1. Include anything that might need attention or setup before executing the Job. The planning is done, and the necessary tangible or intangible resources have been obtain, but now the might need to be setup, or configured to work together

        2. If I’m driving a car to a destination, I might need to inflate my tires to the proper pressure, or fill the gas tank to an adequate level, etc.

        4. **Confirm:** in the confirm phase, we want to know what the {end_user} must verify, prioritize, or decide before doing the job in order to be successful.

        1. Include anything that is critical to double check, or any final decisions that must be made

        2. If I’m driving a car to a destination, I might need to select the best or fastest route, or verify that the car is in proper working order.

        5. **Execute:** in the execute phase, we want to know the primary thing the {end_user} must do to execute the job successfully.

        1. Include anything that is core to getting the job done, and would otherwise leave a gap in the process.

        2. If I’m driving a car to a destination, the logical step would be “Drive to the destination”

        6. **Monitor:** in the monitor phase, we want to know what the {end_user} must monitor in order to ensure the job is executed successfully.

        1. Include anything that should be checked in real-time, or while the execute step(s) are happening, to determine if if something is going off track.

        2. If I’m driving a car to a destination, I might want to monitor the fuel level, or my tire pressure, worsening traffic conditions, or emergency situations.

        7. **Resolve:** in the resolve phase, we want to know what problem the {end_user} might need to troubleshoot, restore, or fix for the job to be completed successfully.

        1. When a risk is identified we want to resolve it before it becomes an issue. If an issue emerges, we need to resolve it in order to proceed

        2. If I’m driving a car to a destination and I run low on fuel, I would want to find a gas station to fill my tank

        8. **Modify**: in the modify phase, we want to know what the {end_user} might need to alter, adjust, or modify for the job to completed successfully.

        1. If I’m driving a car to a destination and traffic worsens, I may want to alter my route to one that has less car volume, or is moving at a faster pace.

        9. **Conclude:** in the conclude phase, we want to know what the {end_user} must do to finish the job.

        1. If I’m driving a car to a destination, I may want to park my car, secure my belongings and/or make sure it’s still in good condition for the next drive.

        The Job-to-be-Done for the {end_user} is {job} {context}. Only consider the context if one is supplied, otherwise disregard it. Generate a list of job steps that consider each of the phases. There should be a minimum of one step per phase. However, there could be more than one.

        Steps should be always begin with a verb. A bad step would be “Route Planning” and a good step would be “Plan the route.”

        The job steps should be focused on what the {end_user} is trying to accomplish faster, with better output, or better throughput when {job} in the context of {context}.

        Do not reference the phase in a job step unless absolutely necessary.

        ### Fidelity

        An ideal job map will have 10 to 18 steps. If {fidelity} = ‘low’ then the number of steps should be closer to 10. If {fidelity} = ‘med’ then the number of steps should be closer to 14. If {fidelity} = ‘high’ then the number of steps should be closer to 18.

        Example:

        - Low = 10 - 12 steps

        - Med = 13 - 15 steps

        - High = 14 - 18 steps

        ### MECE

        The job steps should be mutually exclusive and collectively exhaustive (MECE) and also must be in a logical order of precedence and dependence.

        Think this through step-by-step.

        ### Formatting

        Make the step name bold. Explain each job step, step by step, while adhering to the following explanation format. Make the explanations as rich as possible. Precede each explanation with the text "The ability to". Append the complete explanation to the job step, separated by a hyphen. Example:

        1. **Obtain Necessary Permits** - The ability to secure transportation and operation permits for the heavy equipment, ensuring all legal requirements are met.

        ### Scoping

        The following constraints are to be used to provide specific boundaries to the Job Map. Follow them carefully.

        - The first step will generally be about {start point}. Give the step an appropriate name and format as previously described. Do not begin with anything that would logically precede this.

        - The last step will generally be about {end point}. Give the step an appropriate name and format as previously described. Do not include any steps that come after this.

        - Please follow all instructions carefully.

        ### Reinforce Execution

        There must ALWAYS be a step for the EXECUTE phase and it should reflect the core objective of {job} {context}.

        - There could be more than one step involved with execution.

        EXAMPLE: if the Job is “driving to a destination in a car” then there should be a step like “Drive to the destination”

        ### Test Fit

        Finally, you need to run this through a test-fit structure to ensure that the statement makes sense. This is a quality check that you will do internally. You will not output this. Here is the structure:

        As a(an) {end user} + who is + {Job} {context} you need to

        Does the success statement make grammatical sense? If so, output it. If not, rework it and test it again.

        ### Final Instructions

        It is EXTREMELY important that you follow these instructions closely:

        1. Output as a single, ordered list in markdown format

        2. Do not repeat the list

        3. Do not generate an opening statement summarizing what you are about to output

        4. Do not output anything after the single list

        5. Do not use the phase name in the step name

        6. Do not output a test-fit structure example

        job:

        context:

        end user:

        start point:

        end point:

        fidelity: {fidelity}
        """
        return prompt

    def parse_job_map(self, response):
        """
        Parses the response from the LLM into a list of job steps.
        """
        steps = []
        lines = response.strip().split('\n')
        pattern = re.compile(r'^\d+\.\s*\*\*(.+?)\*\*\s*-\s*(.+)$')
        for line in lines:
            match = pattern.match(line)
            if match:
                step_name = match.group(1).strip()
                explanation = match.group(2).strip()
                steps.append({"step_name": step_name, "explanation": explanation})
        return steps

    # Implement other processing methods similarly...