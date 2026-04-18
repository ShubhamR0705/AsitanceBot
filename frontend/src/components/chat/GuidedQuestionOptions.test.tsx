import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { getGuidedQuestions, GuidedQuestionOptions } from "./GuidedQuestionOptions";
import type { GuidedQuestion } from "../../types/api";

const question: GuidedQuestion = {
  type: "question",
  question: "Can you browse normal websites without the VPN connected?",
  field: "internet_working",
  input_type: "single_select",
  options: [
    { label: "Yes - normal websites work", value: "yes" },
    { label: "No - internet is down", value: "no" },
    { label: "I am not sure", value: "unknown" },
    { label: "Other", value: "other", requires_text: true }
  ]
};

describe("GuidedQuestionOptions", () => {
  it("submits a structured answer when an option is selected", async () => {
    const onAnswer = vi.fn();
    render(<GuidedQuestionOptions questions={[question]} onAnswer={onAnswer} />);

    await userEvent.click(screen.getByRole("button", { name: "Yes - normal websites work" }));

    expect(onAnswer).toHaveBeenCalledWith("Yes - normal websites work", {
      field: "internet_working",
      value: "yes",
      label: "Yes - normal websites work",
      input_type: "single_select",
      question: "Can you browse normal websites without the VPN connected?"
    });
  });

  it("falls back to free text for Other", async () => {
    const onAnswer = vi.fn();
    render(<GuidedQuestionOptions questions={[question]} onAnswer={onAnswer} />);

    await userEvent.click(screen.getByRole("button", { name: "Other" }));
    await userEvent.type(screen.getByPlaceholderText("Type the details instead"), "It works only on mobile hotspot");
    await userEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(onAnswer).toHaveBeenCalledWith("It works only on mobile hotspot");
  });

  it("parses guided questions from message metadata", () => {
    expect(getGuidedQuestions({ structured_questions: [question] })).toEqual([question]);
    expect(getGuidedQuestions({ structured_questions: [{ type: "note" }] })).toEqual([]);
  });

  it("builds guided questions from legacy clarification metadata", () => {
    const parsed = getGuidedQuestions({
      questions: ["Which device and OS are you using, such as Windows laptop or macOS?"],
      missing_fields: ["device_os", "error_message"]
    });

    expect(parsed).toHaveLength(1);
    expect(parsed[0].field).toBe("device_os");
    expect(parsed[0].options.map((option) => option.label)).toContain("Ubuntu/Linux");
  });

  it("does not render generic yes/no options for service selection questions", () => {
    const parsed = getGuidedQuestions({
      structured_questions: [
        {
          type: "question",
          question: "Which application or company service are you trying to access?",
          field: "affected_app",
          input_type: "single_select",
          options: [
            { label: "Yes", value: "yes" },
            { label: "No", value: "no" },
            { label: "Not sure", value: "unknown" },
            { label: "Other", value: "other", requires_text: true }
          ]
        }
      ]
    });

    expect(parsed).toEqual([]);
  });

  it("builds service options from legacy app clarification metadata", () => {
    const parsed = getGuidedQuestions({
      questions: ["Which application or company service are you trying to access?"],
      missing_fields: ["affected_app", "error_message"]
    });

    expect(parsed).toHaveLength(1);
    expect(parsed[0].field).toBe("affected_app");
    expect(parsed[0].options.map((option) => option.label)).toEqual(
      expect.arrayContaining(["Email (Outlook/Gmail)", "VPN", "Company Portal", "Internal Tool", "HR System"])
    );
  });
});
