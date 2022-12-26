function FindFirstNotEqual {
    param ($collection, $neValue)
    foreach ($e in $collection) {
		if ($e -ne $neValue) {
			$e
			break
		}
	}
}
Export-ModuleMember -Function * -Alias *
