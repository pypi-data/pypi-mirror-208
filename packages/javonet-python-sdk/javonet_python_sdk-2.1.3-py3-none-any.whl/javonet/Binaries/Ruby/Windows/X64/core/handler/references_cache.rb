require_relative '../../external_lib/securerandom'

class ReferencesCache

  @instance = new
  @@references_cache = Hash.new

  private_class_method :new

  def self.instance
    @instance
  end
  def cache_reference(object_reference)
    uuid_ = SecureRandom.uuid
    @@references_cache[uuid_] = object_reference
    return uuid_
  end

  def resolve_reference(guid)
    if @@references_cache[guid] == nil
      raise 'Unable to resolve reference with id: ' + guid.to_s
    else
      return @@references_cache[guid]
    end
  end

  def delete_reference(guid)
    if @@references_cache[guid] == nil
      raise 'Object not found in reference cache'
    else
      @@references_cache.delete(guid)
      return 0
    end
  end
end