process SourceCodeEdit {
	sequence Compilation {
		action FileEdit manual {
			agent { "PEOS user" }
			script { "creation and modification of source code files" }
			tool { "editor" }
		}

		action SpellCheck executable {
			agent { "PEOS user" }
			script { "spell checks the modified files" }
			tool { "spell checker" }
			input { "filename" }
			output { "correctly spelled file" }
		}

		action Compile executable {
			agent { "PEOS user" }
			script { "compiles the source code" }
			tool { "make, welder" }
			input { "file.body, file.wtmpl" }
			output { "file.html" }
		}
			
		action Verify manual {
			agent { "PEOS user" }
			script { "verifies the modified file for content" }
			tool { "web browser" }
			input { "html file" }
			provides { "correctly updated source code" }
		}
	}
}
