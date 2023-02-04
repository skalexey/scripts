test = { t = 123 };
print( "Test: ", test.t);

local define = function()
	local m = {};
	setmetatable(m, {
		__index = function(t, key)
			local foundBegin, foundEnd = key:find("GetDataProviderInfo");
			if foundBegin then
				print( "Found: ", foundEnd)
				local label = key:sub(foundEnd);
				return function()
					t:GetDataProviderInfo( label );
				end;
			else
				return t[key];
			end
		end;
	});
	m.GetDataProviderInfo = function( self, label )
		print( "GetDataProviderInfo(", label, ")" );
	end;
	m.test = "111";
	m.TestFunc = function( self, arg )
		print( "TestFunc(", arg, ")", self.test + arg );
	end;
	return m;
end;

local s = {a = 1, b = 2, a = 3}; -- a is overwritten

print( "s.a = ", s.a );

local s = "aa";
if string.find( s, "", 1, true ) then
	print( "Found" );
else
	print( "Not found" );
end