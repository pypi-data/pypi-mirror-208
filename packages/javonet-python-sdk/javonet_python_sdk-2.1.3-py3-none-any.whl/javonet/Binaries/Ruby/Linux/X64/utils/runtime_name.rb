module RuntimeName
  CLR = 0
  GO = 1
  JVM = 2
  NETCORE = 3
  PERL = 4
  PYTHON = 5
  RUBY = 6
  NODEJS = 7

  def self.get_name(runtime_number)
    if runtime_number == 0
      return 'CLR'
    end
    if runtime_number == 1
      return 'GO'
    end
    if runtime_number == 2
      return 'JVM'
    end
    if runtime_number == 3
      return 'NETCORE'
    end
    if runtime_number == 4
      return 'PERL'
    end
    if runtime_number == 5
      return 'PYTHON'
    end
    if runtime_number == 6
      return 'RUBY'
    end
    if runtime_number == 7
      return 'NODEJS'
    end
  end
end
