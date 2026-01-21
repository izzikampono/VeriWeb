import os
import json

from tqdm import tqdm


class Submission(object):
    def __init__(self, answer, actions):
        self.answer = answer
        self.actions = actions


class AgentWorkflowBenchmark:
    NUM_SECONDS_TO_SLEEP = 5
    MAX_TOKENS = 20

    def __init__(self, data_dir):

        self.data_dir = data_dir
        self.data = {}

        self.submit_required = True
        self.scores = {}
        self.responses = []

        self.load_data()

    def load_data(self):
        with open(os.path.join(self.data_dir, "original-20260121.json"), 'r') as f:
            try:
                records = json.load(f)
                for record in records:
                    self.data[record["folder"]] = record
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return
        print(f"A total of {len(self.data)} tasks loaded from {self.data_dir}")

    def _first_sub_tasks(self, content):
        subs = content.get("sub_tasks", [])
        return subs[:1]

    def _context_from_subs(self, subs):
        context_sections = []
        for i, sub in enumerate(subs, start=1):
            context_result = ""
            for x in sub["result"]:
                context_result = context_result + x + "\n"
            context_sections.append(
                f"{sub['instruct']}\nResult: {context_result}"
            )
        return "Results from preliminary subtasks are provided for context:\n" + "\n".join(context_sections)

    def __iter__(self):
        for task_id, (name, content) in enumerate(self.data.items()):
            # global accuracy: only validate the final result
            metadata = {
                "id": name,
                "instruction": content["instruct"],
                "type": "global",
                "task_id": task_id,
            }
            ground_truth = content["result"]
            yield metadata, ground_truth

            subs = self._first_sub_tasks(content)
            instructs = [sub["instruct"] for sub in subs]
            results = []
            for sub in subs:
                results.extend(sub["result"])
            metadata = {
                "id": name + "_only_sub1",
                "instruction": "\n\n".join(instructs),
                "type": "only_sub1",
                "task_id": task_id,
            }
            yield metadata, results

            context = self._context_from_subs(subs)
            result = [x for x in content.get("result", []) if x != ""]
            metadata = {
                "id": name + "_with_sub1_result",
                "instruction": content.get("instruct", "") + "\n" + context,
                "type": "with_sub1_result",
                "task_id": task_id,
            }
            yield metadata, result


if __name__ == '__main__':
    benchmark = AgentWorkflowBenchmark(data_dir='./data')
    dataset = []
    only_sub1_dataset = []
    with_sub1_result_dataset = []
    for i, (metadata, ground) in tqdm(enumerate(benchmark)):
        entry = {
            "id": metadata["task_id"],
            "name": metadata["id"],
            "type": metadata["type"],
            "instruction": metadata["instruction"],
            "answer": json.dumps(ground, ensure_ascii=False),
        }
        if metadata["type"] == "global":
            dataset.append(entry)
        elif metadata["type"] == "only_sub1":
            only_sub1_dataset.append(entry)
        elif metadata["type"] == "with_sub1_result":
            with_sub1_result_dataset.append(entry)

    # save dataset to json file
    with open("data/data-20260121.json", "w") as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)

    with open("data/data-only-sub1-20260121.json", "w") as f:
        json.dump(only_sub1_dataset, f, indent=4, ensure_ascii=False)

    with open("data/data-with-sub1-result-20260121.json", "w") as f:
        json.dump(with_sub1_result_dataset, f, indent=4, ensure_ascii=False)
