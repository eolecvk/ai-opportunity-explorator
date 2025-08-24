// --- CREATE ALL NODES FIRST USING MERGE TO ENSURE UNIQUENESS ---

// Industry Nodes
MERGE (b:Industry {name: 'Banking'})
MERGE (i:Industry {name: 'Insurance'})

// Sector Nodes
MERGE (rb:Sector {name: 'Retail Banking', type: 'consumer'})
MERGE (cb:Sector {name: 'Commercial Banking', type: 'corporate'})
MERGE (ib:Sector {name: 'Investment Banking', type: 'corporate'})
MERGE (pb:Sector {name: 'Private Banking', type: 'consumer'})
MERGE (cu:Sector {name: 'Credit Unions', type: 'consumer'})
MERGE (ob:Sector {name: 'Online Banking', type: 'digital'})
MERGE (li:Sector {name: 'Life Insurance', type: 'consumer'})
MERGE (hi:Sector {name: 'Health Insurance', type: 'consumer'})
MERGE (pi:Sector {name: 'Property Insurance', type: 'consumer'})
MERGE (ci:Sector {name: 'Casualty Insurance', type: 'consumer'})

// Project Nodes
MERGE (p1:Project {
  title: 'Advanced Credit Scoring & Risk Assessment',
  description: 'ML models analyze diverse data sources (transactions, credit reports, alternative data) to create more accurate, fair credit scoring systems and loan default predictions.',
  priority: 'critical',
  implementation_cost: 950,
  ongoing_cost: 170
})
MERGE (p2:Project {
  title: 'Real-Time Fraud Detection & Prevention',
  description: 'Comprehensive fraud prevention across all channels - credit cards, digital payments, transactions, and loan applications - using pattern recognition and anomaly detection.',
  priority: 'critical',
  implementation_cost: 1400,
  ongoing_cost: 250
})
MERGE (p3:Project {
  title: 'Intelligent Customer Service Platform',
  description: '24/7 chatbots, virtual assistants, and voice recognition systems providing comprehensive customer support, account management, and transaction processing.',
  priority: 'high',
  implementation_cost: 800,
  ongoing_cost: 130
})
MERGE (p4:Project {
  title: 'Intelligent Claims Processing & Automation',
  description: 'End-to-end claims automation including intake, assessment, document processing with OCR, and approval workflows reducing processing time from days to hours.',
  priority: 'critical',
  implementation_cost: 1100,
  ongoing_cost: 220
})

// Role Nodes (formerly Person)
MERGE (ds:Role {name: 'Data Scientist'})
MERGE (ai:Role {name: 'AI Engineer'})
MERGE (devops:Role {name: 'DevOps Engineer'})
MERGE (mlOps:Role {name: 'MLOps Engineer'})

// --- CREATE RELATIONSHIPS BETWEEN HIGH-LEVEL NODES ---

// Industry to Sector
MERGE (b)-[:HAS_SECTOR]->(rb)
MERGE (b)-[:HAS_SECTOR]->(cb)
MERGE (b)-[:HAS_SECTOR]->(ib)
MERGE (b)-[:HAS_SECTOR]->(pb)
MERGE (b)-[:HAS_SECTOR]->(cu)
MERGE (b)-[:HAS_SECTOR]->(ob)
MERGE (i)-[:HAS_SECTOR]->(li)
MERGE (i)-[:HAS_SECTOR]->(hi)
MERGE (i)-[:HAS_SECTOR]->(pi)
MERGE (i)-[:HAS_SECTOR]->(ci)

// Sector to Project
MERGE (rb)-[:HAS_PROJECT]->(p1)
MERGE (ob)-[:HAS_PROJECT]->(p2)
MERGE (rb)-[:HAS_PROJECT]->(p3)
MERGE (ob)-[:HAS_PROJECT]->(p3)
MERGE (hi)-[:HAS_PROJECT]->(p4)

// Project to Role
MERGE (p1)-[:REQUIRES_ROLE]->(ds)
MERGE (p1)-[:REQUIRES_ROLE]->(mlOps)
MERGE (p2)-[:REQUIRES_ROLE]->(ai)
MERGE (p2)-[:REQUIRES_ROLE]->(devops)
MERGE (p3)-[:REQUIRES_ROLE]->(ai)
MERGE (p3)-[:REQUIRES_ROLE]->(mlOps)
MERGE (p4)-[:REQUIRES_ROLE]->(ai)
MERGE (p4)-[:REQUIRES_ROLE]->(devops)

// ----------------------------------------------------
// PROJECT-SPECIFIC MODULES AND DEPENDENCIES
// ----------------------------------------------------

// Advanced Credit Scoring & Risk Assessment (Project p1)
MERGE (a1:Module {id: "p1-A", name: "Data Foundation & Integration"})
MERGE (b1:Module {id: "p1-B", name: "Feature Engineering Module"})
MERGE (c1:Module {id: "p1-C", name: "Credit Scoring Model (Baseline)"})
MERGE (d1:Module {id: "p1-D", name: "Loan Default Prediction Engine"})
MERGE (e1:Module {id: "p1-E", name: "Fairness & Bias Mitigation Layer"})
MERGE (f1:Module {id: "p1-F", name: "Model Monitoring & Drift Detection"})
MERGE (p1)-[:HAS_MODULE]->(a1)
MERGE (p1)-[:HAS_MODULE]->(b1)
MERGE (p1)-[:HAS_MODULE]->(c1)
MERGE (p1)-[:HAS_MODULE]->(d1)
MERGE (p1)-[:HAS_MODULE]->(e1)
MERGE (p1)-[:HAS_MODULE]->(f1)
MERGE (a1)-[:LEADS_TO]->(b1)
MERGE (b1)-[:LEADS_TO]->(c1)
MERGE (b1)-[:LEADS_TO]->(d1)
MERGE (c1)-[:LEADS_TO]->(e1)
MERGE (c1)-[:LEADS_TO]->(f1)
MERGE (d1)-[:LEADS_TO]->(f1)

// Real-Time Fraud Detection & Prevention (Project p2)
MERGE (a2:Module {id: "p2-A", name: "Streaming Data Ingestion Layer"})
MERGE (b2:Module {id: "p2-B", name: "Rule-Based Engine Upgrade"})
MERGE (c2:Module {id: "p2-C", name: "Anomaly Detection Model"})
MERGE (d2:Module {id: "p2-D", name: "Alert Prioritization & Explainability"})
MERGE (e2:Module {id: "p2-E", name: "Channel-Specific Fraud Modules"})
MERGE (f2:Module {id: "p2-F", name: "Case Management Dashboard"})
MERGE (p2)-[:HAS_MODULE]->(a2)
MERGE (p2)-[:HAS_MODULE]->(b2)
MERGE (p2)-[:HAS_MODULE]->(c2)
MERGE (p2)-[:HAS_MODULE]->(d2)
MERGE (p2)-[:HAS_MODULE]->(e2)
MERGE (p2)-[:HAS_MODULE]->(f2)
MERGE (a2)-[:LEADS_TO]->(b2)
MERGE (b2)-[:LEADS_TO]->(c2)
MERGE (c2)-[:LEADS_TO]->(d2)
MERGE (c2)-[:LEADS_TO]->(e2)
MERGE (c2)-[:LEADS_TO]->(f2)

// Intelligent Customer Service Platform (Project p3)
MERGE (a3:Module {id: "p3-A", name: "Chatbot for FAQs"})
MERGE (b3:Module {id: "p3-B", name: "Virtual Assistant for Transactions"})
MERGE (c3:Module {id: "p3-C", name: "Omnichannel Integration"})
MERGE (d3:Module {id: "p3-D", name: "Sentiment Analysis & Escalation"})
MERGE (e3:Module {id: "p3-E", name: "Voice Recognition Add-On"})
MERGE (f3:Module {id: "p3-F", name: "Agent Assist Tools"})
MERGE (p3)-[:HAS_MODULE]->(a3)
MERGE (p3)-[:HAS_MODULE]->(b3)
MERGE (p3)-[:HAS_MODULE]->(c3)
MERGE (p3)-[:HAS_MODULE]->(d3)
MERGE (p3)-[:HAS_MODULE]->(e3)
MERGE (p3)-[:HAS_MODULE]->(f3)
MERGE (a3)-[:LEADS_TO]->(b3)
MERGE (b3)-[:LEADS_TO]->(c3)
MERGE (a3)-[:LEADS_TO]->(d3)
MERGE (b3)-[:LEADS_TO]->(e3)
MERGE (d3)-[:LEADS_TO]->(f3)

// Intelligent Claims Processing & Automation (Project p4)
MERGE (a4:Module {id: "p4-A", name: "Claims Intake Portal"})
MERGE (b4:Module {id: "p4-B", name: "OCR & Document Processing"})
MERGE (c4:Module {id: "p4-C", name: "Claims Triage & Routing"})
MERGE (d4:Module {id: "p4-D", name: "Approval Workflow Engine"})
MERGE (e4:Module {id: "p4-E", name: "Assessment Models"})
MERGE (f4:Module {id: "p4-F", name: "Claims Analytics Dashboard"})
MERGE (p4)-[:HAS_MODULE]->(a4)
MERGE (p4)-[:HAS_MODULE]->(b4)
MERGE (p4)-[:HAS_MODULE]->(c4)
MERGE (p4)-[:HAS_MODULE]->(d4)
MERGE (p4)-[:HAS_MODULE]->(e4)
MERGE (p4)-[:HAS_MODULE]->(f4)
MERGE (a4)-[:LEADS_TO]->(b4)
MERGE (b4)-[:LEADS_TO]->(c4)
MERGE (c4)-[:LEADS_TO]->(d4)
MERGE (b4)-[:LEADS_TO]->(e4)
MERGE (c4)-[:LEADS_TO]->(f4)
