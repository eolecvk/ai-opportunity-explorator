// --- BANKING INDUSTRY ---

// Create the main Industry node for Banking.
MERGE (b:Industry {name: 'Banking'})

// Create the intermediate Sector nodes for Banking with a 'type' property.
CREATE (rb:Sector {name: 'Retail Banking', type: 'consumer'})
CREATE (cb:Sector {name: 'Commercial Banking', type: 'corporate'})
CREATE (ib:Sector {name: 'Investment Banking', type: 'corporate'})
CREATE (pb:Sector {name: 'Private Banking', type: 'consumer'})
CREATE (cu:Sector {name: 'Credit Unions', type: 'consumer'})
CREATE (ob:Sector {name: 'Online Banking', type: 'digital'})

// Create relationships from the Banking Industry to its Sectors.
CREATE (b)-[:HAS_SECTOR]->(rb)
CREATE (b)-[:HAS_SECTOR]->(cb)
CREATE (b)-[:HAS_SECTOR]->(ib)
CREATE (b)-[:HAS_SECTOR]->(pb)
CREATE (b)-[:HAS_SECTOR]->(cu)
CREATE (b)-[:HAS_SECTOR]->(ob)

// Create the Project nodes for the Banking industry.

// Advanced Credit Scoring & Risk Assessment project
CREATE (p1:Project {
  title: 'Advanced Credit Scoring & Risk Assessment',
  description: 'ML models analyze diverse data sources (transactions, credit reports, alternative data) to create more accurate, fair credit scoring systems and loan default predictions.',
  priority: 'critical',
  implementation_cost: 950,
  ongoing_cost: 170
});

// Real-Time Fraud Detection & Prevention project
CREATE (p2:Project {
  title: 'Real-Time Fraud Detection & Prevention',
  description: 'Comprehensive fraud prevention across all channels - credit cards, digital payments, transactions, and loan applications - using pattern recognition and anomaly detection.',
  priority: 'critical',
  implementation_cost: 1400,
  ongoing_cost: 250
});

// Intelligent Customer Service Platform project
CREATE (p3:Project {
  title: 'Intelligent Customer Service Platform',
  description: '24/7 chatbots, virtual assistants, and voice recognition systems providing comprehensive customer support, account management, and transaction processing.',
  priority: 'high',
  implementation_cost: 800,
  ongoing_cost: 130
});

// --- INSURANCE INDUSTRY ---

// Create the main Industry node for Insurance.
MERGE (i:Industry {name: 'Insurance'})

// Create the intermediate Sector nodes for Insurance with a 'type' property.
CREATE (li:Sector {name: 'Life Insurance', type: 'consumer'})
CREATE (hi:Sector {name: 'Health Insurance', type: 'consumer'})
CREATE (pi:Sector {name: 'Property Insurance', type: 'consumer'})
CREATE (ci:Sector {name: 'Casualty Insurance', type: 'consumer'})

// Create relationships from the Insurance Industry to its Sectors.
CREATE (i)-[:HAS_SECTOR]->(li)
CREATE (i)-[:HAS_SECTOR]->(hi)
CREATE (i)-[:HAS_SECTOR]->(pi)
CREATE (i)-[:HAS_SECTOR]->(ci)

// Create the Project node for the Insurance industry.
// Intelligent Claims Processing & Automation project
CREATE (p4:Project {
  title: 'Intelligent Claims Processing & Automation',
  description: 'End-to-end claims automation including intake, assessment, document processing with OCR, and approval workflows reducing processing time from days to hours.',
  priority: 'critical',
  implementation_cost: 1100,
  ongoing_cost: 220
});

// Create relationships between Sectors and Projects.
CREATE (rb)-[:HAS_PROJECT]->(p1)
CREATE (ob)-[:HAS_PROJECT]->(p2)
CREATE (rb)-[:HAS_PROJECT]->(p3)
CREATE (ob)-[:HAS_PROJECT]->(p3)
CREATE (hi)-[:HAS_PROJECT]->(p4)

// Create Person nodes with roles
CREATE (ds:Person {name: 'Data Scientist', role: 'Data Scientist'})
CREATE (ai:Person {name: 'AI Engineer', role: 'AI Engineer'})
CREATE (devops:Person {name: 'DevOps Engineer', role: 'DevOps Engineer'})
CREATE (mlOps:Person {name: 'MLOps Engineer', role: 'MLOps Engineer'})

// Assign roles to projects based on required skills
CREATE (p1)-[:REQUIRES_ROLE]->(ds)
CREATE (p1)-[:REQUIRES_ROLE]->(mlOps)

CREATE (p2)-[:REQUIRES_ROLE]->(ai)
CREATE (p2)-[:REQUIRES_ROLE]->(devops)

CREATE (p3)-[:REQUIRES_ROLE]->(ai)
CREATE (p3)-[:REQUIRES_ROLE]->(mlOps)

CREATE (p4)-[:REQUIRES_ROLE]->(ai)
CREATE (p4)-[:REQUIRES_ROLE]->(devops)
