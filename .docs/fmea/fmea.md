
# Key to FMEA Ratings:Severity (S): 
Impact of the failure on the final product/user (1 = Minor inconvenience, 10 = Hazardous/Catastrophic loss of archival record).Occurrence (O): How frequently the cause is likely to happen (1 = Very unlikely, 10 = Almost inevitable).Detection (D): How likely the current controls will detect the failure before it reaches the customer/archive (1 = Almost certain to detect, 10 = Undetectable).RPN (Risk Priority Number): $\text{S} \times \text{O} \times \text{D}$. Used to prioritize actions. A higher RPN indicates a higher risk that needs immediate attention.

FMEA Key Advanced Concepts Explained

1. Structure Analysis (Step 2)

- Process Step (Element) & Work Element (Focus Element): Breaks down the process to a specific work element (e.g., "Load Part" is the Element; "Operator places part into fixture" is the Focus Element). This provides a more granular basis for analysis.

- 4M Category: Links the failure cause to a major category: Man, Machine, Material, or Method. This helps structure root cause brainstorming and action assignment.

2. Function Analysis (Step 3)

Focuses on requirements for the functions, using the structure: "Element" $\rightarrow$ "Function" $\rightarrow$ "Requirement".

3. Failure Chain (Step 4)

- Emphasizes the link: Cause (FC) $\rightarrow$ Mode (FM) $\rightarrow$ Effect (FE).
- Potential Failure Effect (FE): What the customer experiences (internal/external).
- Potential Failure Mode (FM): The way the function/requirement fails (e.g., "Too loose," "Not aligned").
- Potential Failure Cause (FC): The root cause leading to the failure mode (e.g., "Operator selected wrong setting").

4. Risk Analysis (Step 5)

- Severity (S), Occurrence (O), and Detection (D): These are still rated, typically on a 1-10 scale, but with updated criteria tables defined in the AIAG-VDA handbook.

- Action Priority (AP): This replaces the RPN. The AP is determined by a look-up table based on the combination of S, O, and D ratings. It indicates the priority for action, not just a mathematical score.

    -H (High): Action to improve Prevention/Detection controls (or justification for no action) MUST be taken.

    - M (Medium): Action SHOULD be taken.
    
    - L (Low): Action COULD be taken.
    
    
5. Optimization (Step 6) & Results (Step 7)

This section focuses on the risk reduction plan and its effectiveness.

Recommended Action(s): Actions should target the Cause (FC) to improve Prevention (reduce Occurrence) or the Failure Mode (FM) to improve Detection.

New S/O/D/AP: After the action is implemented, the team re-evaluates the ratings to calculate the residual risk (New AP). The Severity rating (S) can typically only be reduced by a design or process change, not a control.