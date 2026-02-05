import warnings
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality isn't compatible", module="groq._compat")


import streamlit as st
from agents.planner import get_planner
from agents.executor import get_executor
from agents.verifier import get_verifier

st.title("AI Ops Assistant")
st.markdown("An intelligent assistant that can fetch weather, news, and jokes based on your queries.")

# User input
query = st.text_input("Enter your query:", placeholder="e.g., What's the weather in New York and tell me a joke?")

if st.button("Execute Query"):
    if not query.strip():
        st.error("Please enter a valid query.")
    else:
        with st.spinner("Planning your request..."):
            planner = get_planner()
            plan = planner.create_plan(query)
        
        if plan.get("error"):
            st.error(f"Planning failed: {plan['error']}")
        else:
            st.success(f"Plan created with {len(plan.get('steps', []))} steps.")
            with st.expander("View Plan Details"):
                st.json(plan)
            
            with st.spinner("Executing the plan..."):
                executor = get_executor()
                execution_result = executor.execute_plan(plan)
            
            st.info(f"Execution completed: {execution_result['steps_completed']}/{execution_result['total_steps']} steps successful.")
            
            with st.spinner("Formatting results..."):
                verifier = get_verifier()
                result = verifier.verify_and_format(query, execution_result['step_results'])
            
            # Display the formatted answer
            st.markdown("### Response")
            st.markdown(result['formatted_answer'])
            
            # Show additional info if available
            if result.get('failed_steps'):
                with st.expander("Failed Steps"):
                    for step in result['failed_steps']:
                        st.write(f"- {step.get('action')}: {step.get('error')}")
            
            if result.get('suggestions'):
                with st.expander("Suggestions"):
                    for suggestion in result['suggestions']:
                        st.write(f"- {suggestion}")
                        
                        
 # in the footer and fixed footer alignment issue fix in center
st.markdown("<style>footer {position: fixed;left: 0;  width: 100%; bottom: 0;  text-align: center;background: black; color: white; padding: 5px 20;}</style>", unsafe_allow_html=True)
st.markdown("<footer style='text-align: center; margin-top: 20px;'>Your search for the 'Best Match' ends here — Crafted with ❤️ by kaushalkrgupta02.</footer>", unsafe_allow_html=True)