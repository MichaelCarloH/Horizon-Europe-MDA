'use client'
import Section from "./components/section";
import TeamFaceRecognition from "./components/teamPicture";

export default function Home() {
    return (
      <main>
       <Section 
                title={"What we do?"}
                paragraph={"At Learning Rate, we are dedicated to demystifying machine learning for beginners. Our mission is to provide comprehensive, easy-to-understand online lessons that cover all the foundational concepts of machine learning. Whether you're new to the field or looking to solidify your understanding, our lessons are designed to guide you through the basics and prepare you for more advanced topics."}
                image={"/lightBulb.jpeg"} imgW={500} imgH={500} alternative={"An icon of a lightbulb to represent learning and ideas."} 
                leftToRight={true}     
        />
        <Section 
                title={"Why Do We Do This?"}
                paragraph={"We believe that machine learning is a pivotal skill for the future, and everyone should have the opportunity to learn it. Our goal is to make machine learning accessible to all students, regardless of their background or prior knowledge. By providing a free, interactive, and supportive learning environment, we aim to inspire a new generation of innovators and problem solvers."}
                image={"/heart.jpeg"} imgW={500} imgH={500} alternative={"An icon of a heart to symbolize passion and dedication.  A graphic showing diverse people collaborating.  An illustration of a rocket to signify ambition and progress."}
                leftToRight={false} 
        />
        <Section 
                title={"How We Do It?"}
                paragraph={"Our approach combines theoretical lessons with hands-on practice. After completing our detailed lessons, students can experiment with our interactive playground. Here, they can build, train, and test their own neural networks using our pre-made training sets. This practical experience allows students to learn from their mistakes and understand the inner workings of machine learning algorithms. Our platform is designed to be user-friendly, encouraging experimentation and discovery."}
                image={"/personComputer.jpeg"} imgW={500} imgH={500} alternative={"A graphic of a computer screen with code or a neural network visualization."} 
                leftToRight={true}     
        />
        <TeamFaceRecognition/>
      </main>
    );
  };