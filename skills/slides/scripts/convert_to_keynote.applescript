on findDocumentForPath(inputPath, inputName, inputStem)
	tell application "Keynote"
		repeat with candidateDocument in documents
			try
				set candidateFile to file of candidateDocument
				if candidateFile is not missing value then
					set candidatePath to POSIX path of (candidateFile as alias)
					if candidatePath is inputPath then return candidateDocument
				end if
			end try
			try
				set candidateName to name of candidateDocument
				if candidateName is inputName or candidateName is inputStem then return candidateDocument
			end try
		end repeat
	end tell
	return missing value
end findDocumentForPath

on run argv
	if (count of argv) is not 2 then
		error "Usage: osascript convert_to_keynote_path_safe.applescript input.pptx output.key"
	end if

	set inputPath to item 1 of argv
	set outputPath to item 2 of argv
	tell application "System Events"
		if not (exists disk item inputPath) then error "Input presentation does not exist: " & inputPath
		if exists disk item outputPath then error "Refusing to overwrite existing output: " & outputPath
		set inputName to name of disk item inputPath
	end tell
	set inputStem to inputName
	if inputName ends with ".pptx" then set inputStem to text 1 thru -6 of inputName

	with timeout of 600 seconds
		tell application "Keynote" to open POSIX file inputPath

		set openedDocument to missing value
		repeat with waitCount from 1 to 120
			set openedDocument to my findDocumentForPath(inputPath, inputName, inputStem)
			if openedDocument is not missing value then exit repeat
			delay 1
		end repeat
		if openedDocument is missing value then error "Could not identify the imported presentation by path or name."

		tell application "Keynote"
			save openedDocument in POSIX file outputPath
			close openedDocument saving no
		end tell
	end timeout
end run
