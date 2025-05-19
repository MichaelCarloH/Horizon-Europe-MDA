import ProjectCard from "./projects-components/project_card";

// Static projects data
const projects = [
    {
        lessonID: 1,
        lessonTitle: "Organization Map Dashboard",
        lessonTag: "Data Visualization",
        lessonDescription: "Interactive dashboard showing European research organizations by topic, with map visualization and detailed statistics.",
        lessonImg: "/Horizon-Europe.png",
        lessonLink: "/projects/org-map-dashboard",
        isLocked: 0
    },
    {
        lessonID: 2,
        lessonTitle: "Research Funding Analysis",
        lessonTag: "Data Analysis",
        lessonDescription: "Analyze funding patterns and trends across different research domains in Europe.",
        lessonImg: "/Horizon-Europe.png",
        lessonLink: "/projects/funding-analysis",
        isLocked: 0
    },
    {
        lessonID: 3,
        lessonTitle: "Collaboration Network",
        lessonTag: "Network Analysis",
        lessonDescription: "Visualize and analyze research collaboration networks between organizations.",
        lessonImg: "/Horizon-Europe.png",
        lessonLink: "/projects/collaboration-network",
        isLocked: 0
    },
    {
        lessonID: 4,
        lessonTitle: "Research Impact Metrics",
        lessonTag: "Analytics",
        lessonDescription: "Track and analyze the impact of research projects using various metrics.",
        lessonImg: "/Horizon-Europe.png",
        lessonLink: "/projects/impact-metrics",
        isLocked: 0
    },
    {
        lessonID: 5,
        lessonTitle: "Project Timeline Tracker",
        lessonTag: "Project Management",
        lessonDescription: "Monitor and visualize project timelines and milestones across different research initiatives.",
        lessonImg: "/Horizon-Europe.png",
        lessonLink: "/projects/timeline-tracker",
        isLocked: 0
    },
    {
        lessonID: 6,
        lessonTitle: "Research Output Dashboard",
        lessonTag: "Data Visualization",
        lessonDescription: "Comprehensive dashboard showing research outputs, publications, and patents.",
        lessonImg: "/Horizon-Europe.png",
        lessonLink: "/projects/output-dashboard",
        isLocked: 0
    }
];

export default function Home() {
    return (
        <main className="flex flex-wrap flex-row justify-center gap-8 m-8">
            {projects.map((project) => (
                <ProjectCard
                    key={project.lessonID}
                    title={project.lessonTitle}
                    tag={project.lessonTag}
                    text={project.lessonDescription}
                    imgLink={project.lessonImg}
                    isLocked={project.isLocked}
                    lessonLink={project.lessonLink}
                />
            ))}
        </main>
    );
}
