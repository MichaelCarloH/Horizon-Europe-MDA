import ProjectCard from "./projects-components/project_card";

// Static projects data
const projects = [
    {
        projectID: 1,
        projectTitle: "Organization Map Dashboard",
        projectTag: "Interactive Map",
        projectDescription: "Interactive dashboard showing European research organizations by topic, with map visualization and detailed statistics.",
        projectImg: "/Europe_map.png",
        projectLink: "/projects/org-map-dashboard",
        isLocked: 0
    },
    {
        projectID: 2,
        projectTitle: "Research Funding Analysis",
        projectTag: "Data Analysis",
        projectDescription: "Analyze funding patterns and trends across different research domains in Europe.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/funding-analysis",
        isLocked: 1
    },
    {
        projectID: 3,
        projectTitle: "Collaboration Network",
        projectTag: "Network Analysis",
        projectDescription: "Visualize and analyze research collaboration networks between organizations.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/collaboration-network",
        isLocked: 1
    },
    {
        projectID: 4,
        projectTitle: "Research Impact Metrics",
        projectTag: "Analytics",
        projectDescription: "Track and analyze the impact of research projects using various metrics.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/impact-metrics",
        isLocked: 1
    },
    {
        projectID: 5,
        projectTitle: "Project Timeline Tracker",
        projectTag: "Project Management",
        projectDescription: "Monitor and visualize project timelines and milestones across different research initiatives.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/timeline-tracker",
        isLocked: 1
    },
    {
        projectID: 6,
        projectTitle: "Research Output Dashboard",
        projectTag: "Data Visualization",
        projectDescription: "Comprehensive dashboard showing research outputs, publications, and patents.",
        projectImg: "/coming_soon.png",
        projectLink: "/projects/output-dashboard",
        isLocked: 1
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
                />
            ))}
        </main>
    );
}
