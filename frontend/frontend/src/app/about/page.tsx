'use client'
import Section from "./components/section";

export default function Home() {
    return (
      <main className="py-8">
       <Section 
                title={"What we do?"}
                paragraph={"At EuroRAG, we make EU research funding accessible to everyone through our AI-powered chatbot and interactive visualization tools. Our system processes and analyzes the CORDIS dataset, transforming complex project documentation into clear, actionable insights. Through our chatbot, users can ask questions in natural language about any aspect of Horizon Europe projects, from specific research initiatives to broad funding patterns, and receive precise, data-driven answers instantly. Additionally, our suite of interactive projects and visualizations helps you explore and understand the European research landscape through maps, networks, and analytics dashboards. Think of it as having both an expert research consultant and powerful analytical tools at your fingertips, making EU research funding transparent and accessible 24/7."}
                image={"/compass.png"} imgW={500} imgH={500} 
                alternative={"An illustration showing innovative thinking and collaboration, with a central lightbulb surrounded by various research and technology icons."} 
                leftToRight={true}     
        />
        <Section 
                title={"Why Do We Do This?"}
                paragraph={"The Horizon Europe program represents billions of euros in research funding, yet understanding this vast ecosystem of projects, partnerships, and opportunities remains a challenge. Many valuable insights remain hidden in complex documentation and disconnected databases. We are changing this by breaking down information barriers and democratizing access to EU research knowledge. Whether you are a researcher seeking collaboration opportunities, a policymaker analyzing funding impact, or a citizen interested in EU-funded innovation, we believe everyone should have equal access to understanding how European research shapes our future."}
                image={"/stakeholders.png"} imgW={500} imgH={500} 
                alternative={"An illustration representing the mission of EU research collaboration, showing people connected through a central heart symbol surrounded by research and innovation icons."} 
                leftToRight={false} 
        />
        <Section 
                title={"How We Do It?"}
                paragraph={"Our system leverages cutting-edge RAG (Retrieval-Augmented Generation) technology to provide accurate, context-aware responses. We process and index the extensive CORDIS dataset, which contains detailed information about all EU-funded research projects. When you ask a question, our self-query system analyzes your intent and automatically structures the query to find the most relevant information. Finally, our RAG system combines the retrieved information with large language model capabilities to generate comprehensive, fact-based responses that are always grounded in official EU project data. To complement our chatbot, we offer a suite of specialized tools and visualizations in our Projects section. These include an interactive European Research Organization Map (currently available), along with several exciting tools in development: funding analysis tools, collaboration network visualizations, impact metrics tracking, project timeline monitoring, and comprehensive research output dashboards. These tools are designed to help you explore and understand the European research landscape from different angles, whether you are interested in geographical distribution, funding patterns, collaboration networks, or research outcomes. We are actively working on bringing these additional features to you soon."}
                image={"/step_by_step.png"} imgW={500} imgH={500} 
                alternative={"A technological illustration showing a person interacting with a computer system, surrounded by gears and digital elements representing the AI-powered search and analysis capabilities."} 
                leftToRight={true}     
        />
      </main>
    );
  };