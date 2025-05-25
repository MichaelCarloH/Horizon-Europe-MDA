import ProjectCard from "./projects-components/project_card";

// Static projects data
const projects = [
    {
        projectID: 1,
        projectTitle: "Organizations by Research Area Dashboard",
        projectTag: "Which organizations are the centers of expertise in the EU?",
        projectDescription: "Find out via this interactive dashboard showing European research organizations by research topic, with map visualizations and detailed statistics.",
        projectImg: "/Europe_map.png",
        projectLink: "/projects/org-map-dashboard",
        isLocked: 0,
        buttonText: "Interactive Map"
    },
    {
        projectID: 2,
        projectTitle: "Research Funding Analysis",
        projectTag: "How are EU funds distributed across research areas?",
        projectDescription: "Get insights on funding patterns and trends across different research domains of projects in the Horizon Europe program.",
        projectImg: "/bargraph.jpg",
        projectLink: "/projects/funding-analysis",
        isLocked: 0,
        buttonText: "View Analysis"
    },
    {
        projectID: 3,
        projectTitle: "Research Impact Metrics Dashboard",
        projectTag: "What's the impact of research projects across the Horizon Europe program?",
        projectDescription: "We analyzed and visualized the impact of organizations involved and their projects in the Horizon Europe program ",
        projectImg: "/compass.png",
        projectLink: "/projects/research-impact-metrics",
        isLocked: 0,
        buttonText: "View Metrics"
    },
    {
        projectID: 4,
        projectTitle: "Collaboration Networks Analysis",
        projectTag: "Who are the most influential organizations in Horizon Europe?",
        projectDescription: "Explore organization influence in their collaborative networks using centrality measures and visualize their networks with graph interface.",
        projectImg: "/network.jpg",
        projectLink: "/projects/network-analysis",
        isLocked: 0,
        buttonText: "View Network Analysis"
    },
    {
        projectID: 5,
        projectTitle: "Project Timeline Tracker",
        projectTag: "Project Management",
        projectDescription: "Monitor and visualize project timelines and milestones across different research initiatives.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/timeline-tracker",
        isLocked: 1,
        buttonText: "View Timeline"
    },
    {
        projectID: 6,
        projectTitle: "Research Output Dashboard",
        projectTag: "Data Visualization",
        projectDescription: "Comprehensive dashboard showing research outputs, publications, and patents.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/output-dashboard",
        isLocked: 1,
        buttonText: "View Dashboard"
    }
];

export default function Home() {
    return (
        <main className="flex flex-wrap flex-row justify-center gap-8 m-8">
            {projects.map((project) => (
                <ProjectCard
                    key={project.projectID}
                    title={project.projectTitle}
                    tag={project.projectTag}
                    text={project.projectDescription}
                    imgLink={project.projectImg}
                    isLocked={project.isLocked}
                    projectLink={project.projectLink}
                    buttonText={project.buttonText}
                />
            ))}
        </main>
    );
}
